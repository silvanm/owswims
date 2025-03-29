import logging
import json
import re
import os
import sys
import pycountry
import requests
import uuid
from datetime import datetime
from django.conf import settings
from django.utils.text import slugify
from thefuzz import fuzz, process
from typing import Optional, Dict, Any, List, Tuple
from django.core.management.base import OutputWrapper
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

from .scraping_service import ScrapingService
from .geocoding_service import GeocodingService
from app.models import Event, Location, Organizer, Race


def is_running_from_django_q():
    """Check if the code is running from Django Q"""
    # Check if any of the modules in the call stack are from Django Q
    for frame in sys._current_frames().values():
        while frame:
            if frame.f_globals.get("__name__", "").startswith("django_q"):
                return True
            frame = frame.f_back
    return False


# Configure logger
logger = logging.getLogger(__name__)

# Make sure the root logger level is set to INFO
logger.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Check if running from Django Q
if is_running_from_django_q():
    # Add console handler for Django Q tasks
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.info("Running from Django Q - logging to console")
else:
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(settings.BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Create a file handler for the crawler log
    log_file_path = os.path.join(
        logs_dir, f'event_crawler_{datetime.now().strftime("%Y%m%d")}.log'
    )
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)


# Geocoding functionality is now provided by the shared GeocodingService


class EventProcessor:
    """
    Process event URLs to create or update events in the database.

    This class is responsible for:
    1. Scraping content from event URLs
    2. Using LLM to analyze the content and extract structured event data
    3. Creating or updating events, races, locations, and organizers in the database
    """

    def __init__(
        self,
        firecrawl_api_key: str,
        stdout: OutputWrapper = None,
        stderr: OutputWrapper = None,
        dry_run: bool = False,
    ):
        self.scraping_service = ScrapingService(
            api_key=firecrawl_api_key, stdout=stdout, stderr=stderr
        )
        self.llm = OpenAI(model="gpt-4o")
        self.dry_run = dry_run

        logger.info(f"EventProcessor initialized (dry_run={dry_run})")

    def process_event_urls(self, urls: List[str]) -> Optional[Event]:
        """Process a list of URLs that belong to the same event"""
        # Log the URLs being processed
        logger.info(f"Processing event URLs: {', '.join(urls)}")

        # Standard scraping
        contents = []
        for url in urls:
            logger.info(f"Scraping URL: {url}")
            content = self.scraping_service.scrape(url)
            if content:
                contents.append({"url": url, "content": content})
                logger.info(f"Successfully scraped URL: {url}")
            else:
                logger.error(f"Failed to scrape URL: {url}")

        if not contents:
            logger.error("Failed to scrape any URLs")
            return None

        # Create a tool for the LLM to scrape additional pages if needed
        scrape_tool = FunctionTool.from_defaults(fn=self.scraping_service.scrape)
        agent = ReActAgent.from_tools(
            [scrape_tool], max_iterations=20, llm=self.llm, verbose=True
        )

        # Get current date for filtering future events
        from datetime import datetime

        current_date = datetime.now().strftime("%Y-%m-%d")

        # Extract event information using LLM
        prompt = f"""Analyze these pages about an open water swimming event.
Visit the following URLs to gather information about a swim event: {', '.join(urls)}
These URLs contain details about the same event. Please analyze all pages and combine the information to create a complete event profile.

Today's date is {current_date}. Only process events that will take place in the future (after today's date).
If the event has already occurred (before today's date), do not process it.

If the page is not about a single open water swim event, skip it.

If the event has an item "Links" which appears to include more information about it, follow it.

To find out the price of the event, look for the registration page ("Anmeldung" or "Ausschreibung") or the page where you can buy tickets.

If the event is virtual or does not have a physical location, skip it.

Return the information as JSON. The response should be in the following format:
{{
    "event": {{
        "name": "OCEANMAN Phuket 2024",  // Name of the event (Event.name)
        "website": "https://oceanmanswim.com/phuket-thailand/",  // Website of the event (Event.website)
        "date_start": "2024-07-15",  // Start date of the event (Event.date_start)
        "date_end": "2024-07-15",  // End date of the event (Event.date_end)
        "location": {{
            "city": "Phuket",  // City where the event takes place (Location.city)
            "country": "Thailand",  // Country where the event takes place (Location.country)
            "water_name": "Andaman Sea",  // Name of the water body (Location.water_name)
            "water_type": "sea",  // Type of water: river, sea, lake, pool (Location.water_type)
            "address": "123 Beach Road, Phuket"  // Address of the event or name of the beach (Location.address)
        }},
        "organizer": {{
            "name": "OCEANMAN"  // Name of the organizer (Organizer.name)
        }},
        "needs_medical_certificate": true,  // Whether a medical certificate is required (Event.needs_medical_certificate)
        "needs_license": false,  // Whether a license is required (Event.needs_license)
        "sold_out": false,  // Whether the event is sold out (Event.sold_out)
        "cancelled": false,  // Whether the event is cancelled (Event.cancelled)
        "with_ranking": true,  // Whether there is a ranking (Event.with_ranking)
        "water_temp": 28.5,  // Water temperature in Celsius (Event.water_temp)
        "description": "This is a public description of the event." // Public description of the event. Leave
        empty if you don't find one. (Event.description)
    }},
    "races": [ {{
        "name": "10 km Open Water Race",  // Name of the race (Race.name)
        "date": "2024-07-15",  // Date of the race (Race.date)
        "race_time": "09:00:00",  // Time when the race starts (Race.race_time)
        "distance": 10.0,  // Distance of the race in kilometers (Race.distance)
        "wetsuit": "optional",  // Wetsuit requirements: compulsory, optional, prohibited (Race.wetsuit)
        "price": {{
            "amount": 50.0,  // Price to participate in the race (Race.price)
            "currency": "EUR"  // Currency used for the price (Race.price)
        }}
    }}]
}}   

Do not return any comments in the JSON file.

Note: There are multiple races per swim event.
Please analyze all the URLs provided and combine the information to create the most complete event profile possible.
If some data is not found in any of the URLs, return null in the field.
For the wetsuit field, only use one of these values: 'compulsory', 'optional', 'prohibited'.
For the water_type field, only use one of these values: 'river', 'sea', 'lake', 'pool'.
"""
        response = agent.chat(prompt)

        try:
            # Extract JSON from the response
            json_text = response.response
            # Find the JSON content between triple backticks if present
            json_match = re.search(r"```json\s*(.*?)\s*```", json_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)

            data = json.loads(json_text)
            return self._save_event_data(data, urls)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {str(e)}")
            print(json_text)  # Print the text that failed to parse for debugging
            return None
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
            return None

    def _save_event_data(self, data: Dict, urls: List[str]) -> Optional[Event]:
        """Save the processed event data to the database"""
        # Create or get Location
        location_data = data["event"]["location"]

        if self.dry_run:
            logger.info(
                f"[DRY RUN] Would get or create location: {location_data['city']}, {location_data['country']}"
            )
            # Create a dummy location object for dry run
            from collections import namedtuple

            DummyLocation = namedtuple("DummyLocation", ["id", "city", "country"])
            location = DummyLocation(
                id=0, city=location_data["city"], country=location_data["country"]
            )
        else:
            location = self._get_or_create_location(location_data)
            if not location:
                logger.error("Failed to create or find location")
                return None

        # Check if the event is in the future
        from datetime import datetime

        current_date = datetime.now().date()
        event_start_date = datetime.strptime(
            data["event"]["date_start"], "%Y-%m-%d"
        ).date()

        if event_start_date <= current_date:
            logger.info(f"Skipping past event with start date {event_start_date}")
            return None

        # Check if there's already an event at the same location on the same date
        if not self.dry_run:
            existing_events = Event.objects.filter(
                location=location, date_start=data["event"]["date_start"]
            )

            if existing_events.exists():
                logger.info(
                    f"Skipping event '{data['event']['name']}' as there's already an event at {location.city}, {location.country} on {data['event']['date_start']}"
                )
                return None

        # Get or create organizer
        organizer_name = data["event"].get("organizer", {}).get("name", "")
        if self.dry_run:
            logger.info(f"[DRY RUN] Would get or create organizer: {organizer_name}")
            # Create a dummy organizer object for dry run
            from collections import namedtuple

            DummyOrganizer = namedtuple("DummyOrganizer", ["id", "name"])
            organizer = (
                DummyOrganizer(id=0, name=organizer_name) if organizer_name else None
            )
        else:
            organizer = self._get_or_create_organizer(organizer_name)

        # Create Event
        event_data = data["event"]
        try:
            if self.dry_run:
                # Create a dummy event object for dry run
                from collections import namedtuple

                DummyEvent = namedtuple("DummyEvent", ["id", "name"])
                event = DummyEvent(id=0, name=event_data["name"])
                logger.info(f"[DRY RUN] Would create event: {event.name}")
                logger.info(f"[DRY RUN] Event details: {event_data}")
            else:
                event = Event.objects.create(
                    name=event_data["name"],
                    website=event_data.get(
                        "website", urls[0]
                    ),  # Use the first URL as default
                    slug=slugify(event_data["name"]),  # Generate slug from name
                    location=location,
                    organizer=organizer,
                    needs_medical_certificate=event_data.get(
                        "needs_medical_certificate"
                    ),
                    needs_license=event_data.get("needs_license"),
                    sold_out=event_data.get("sold_out"),
                    cancelled=event_data.get("cancelled"),
                    with_ranking=event_data.get("with_ranking"),
                    date_start=event_data["date_start"],
                    date_end=event_data["date_end"],
                    water_temp=event_data.get("water_temp"),
                    description=event_data.get("description") or "",
                )
                logger.info(
                    f"Successfully created event: {event.name} (ID: {event.id})"
                )
        except Exception as e:
            logger.error(f"Failed to create event: {str(e)}")
            return None

        # Create Races
        for race_data in data["races"]:
            try:
                if self.dry_run:
                    logger.info(
                        f"[DRY RUN] Would create race: {race_data['name']} for event: {event.name}"
                    )
                    logger.info(f"[DRY RUN] Race details: {race_data}")
                else:
                    race = Race.objects.create(
                        event=event,
                        name=race_data["name"],
                        date=race_data["date"],
                        race_time=race_data.get("race_time"),
                        distance=race_data["distance"],
                        wetsuit=race_data.get("wetsuit"),
                        price=race_data.get("price", {}).get("amount"),
                    )
                    logger.info(f"Created race: {race.name} for event: {event.name}")
            except Exception as e:
                logger.error(f"Failed to create race: {str(e)}")

        return event

    def _get_or_create_location(self, location_data: Dict) -> Optional[Location]:
        """Get or create a location from the provided data"""
        if not location_data.get("city") or not location_data.get("country"):
            logger.error("Missing city or country in location data")
            return None

        # Convert country name to code
        country = pycountry.countries.get(name=location_data["country"])
        if not country:
            logger.error(f"Could not find country code for {location_data['country']}")
            return None
        country_code = country.alpha_2

        # Try to find an exact match first using all available fields
        location = Location.objects.filter(
            city=location_data["city"],
            country=country_code,
            water_name=location_data.get("water_name"),
            water_type=location_data.get("water_type"),
        ).first()

        if location:
            # Update address if provided and different
            if (
                location_data.get("address")
                and location.address != location_data["address"]
            ):
                location.address = location_data["address"]
                location.save()
            logger.info(f"Using existing location: {location.city}, {location.country}")
            return location

        # If no exact match, create a new location with geocoding
        new_location = Location(
            city=location_data["city"],
            country=country_code,
            water_name=location_data.get("water_name"),
            water_type=location_data.get("water_type"),
            address=location_data.get("address"),
        )
        logger.info(
            f"Creating new location: {new_location.city}, {new_location.country}"
        )

        # Geocode the location using our shared geocoding service
        try:
            # Initialize the geocoding service
            geocoding_service = GeocodingService(stdout=self.stdout, stderr=self.stderr)

            # Geocode the location
            success = geocoding_service.geocode_location(new_location)

            if success:
                # Check for nearby locations (<1km)
                if new_location.lat is not None and new_location.lng is not None:
                    nearby_locations = geocoding_service.get_nearby_locations(
                        new_location.lat, new_location.lng, max_distance_km=1.0
                    )

                    if nearby_locations:
                        # Use the closest existing location instead
                        closest = nearby_locations[0]
                        logger.info(
                            f"Found existing location {closest['location']} {closest['distance']:.2f}km away. "
                            f"Using it instead of creating a new one."
                        )
                        return closest["location"]
            else:
                logger.warning(
                    f"Geocoding failed for {new_location.city}, {country.name}"
                )
        except Exception as e:
            logger.error(f"Error during geocoding: {str(e)}")

        # If we get here, either geocoding failed or no nearby locations were found
        # Save the new location
        try:
            new_location.save()
            logger.info(
                f"Successfully created new location: {new_location.city}, {new_location.country}"
            )

            # Fetch and set header image for the new location if we have coordinates
            if new_location.lat is not None and new_location.lng is not None:
                try:
                    # Use the same geocoding service to find a place and set header image
                    place_details = geocoding_service.find_place_by_location(
                        new_location
                    )

                    if (
                        place_details
                        and "photos" in place_details
                        and place_details["photos"]
                    ):
                        # Get the first photo
                        photo_reference = place_details["photos"][0]["photo_reference"]
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={settings.GOOGLE_MAPS_API_KEY}"

                        # Download and save the image
                        import requests
                        import uuid

                        with requests.get(photo_url, stream=True) as r:
                            if r.status_code == 200:
                                r.raw.seek = lambda x, y: 0
                                r.raw.size = int(r.headers.get("Content-Length", 0))
                                filename = f"location_{new_location.id}_{uuid.uuid4().hex[:8]}.jpeg"

                                # Save the image
                                new_location.header_photo.save(
                                    filename, r.raw, save=True
                                )
                                logger.info(
                                    f"Successfully added header image for location: {new_location.city}"
                                )
                            else:
                                logger.warning(
                                    f"Failed to download image: HTTP {r.status_code}"
                                )
                    else:
                        logger.warning(
                            f"No photos found for location: {new_location.city}"
                        )
                except Exception as e:
                    logger.error(f"Error fetching header image: {str(e)}")
            else:
                logger.warning(
                    f"Cannot fetch header image for location without coordinates: {new_location.city}"
                )

            return new_location
        except Exception as e:
            logger.error(f"Failed to create new location: {str(e)}")
            return None

    def _get_or_create_organizer(self, organizer_name: str) -> Optional[Organizer]:
        """Get or create an organizer using fuzzy matching"""
        if not organizer_name:
            logger.warning("No organizer name provided")
            return None

        # Get all existing organizers
        existing_organizers = Organizer.objects.all()
        # Use fuzzy matching to find the best match
        best_match = process.extractOne(
            organizer_name,
            [org.name for org in existing_organizers],
            scorer=fuzz.token_sort_ratio,
            score_cutoff=80,  # Minimum similarity score (0-100)
        )

        if best_match:
            organizer = existing_organizers.get(name=best_match[0])
            logger.info(f"Using existing organizer: {organizer.name}")
            return organizer
        else:
            # If no good match found, create new organizer
            try:
                organizer = Organizer.objects.create(name=organizer_name)
                logger.info(f"Created new organizer: {organizer.name}")
                return organizer
            except Exception as e:
                logger.error(f"Failed to create new organizer: {str(e)}")
                return None
