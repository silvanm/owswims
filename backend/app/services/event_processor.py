import logging
import json
import re
import pycountry
from django.utils.text import slugify
from thefuzz import fuzz, process
from typing import Optional, Dict, Any, List, Tuple
from django.core.management.base import OutputWrapper
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

from .scraping_service import ScrapingService
from app.models import Event, Location, Organizer, Race


logger = logging.getLogger(__name__)


class EventProcessor:
    """Process event URLs to create or update events in the database"""

    def __init__(self, firecrawl_api_key: str, stdout: OutputWrapper = None, stderr: OutputWrapper = None):
        self.scraping_service = ScrapingService(api_key=firecrawl_api_key, stdout=stdout, stderr=stderr)
        self.llm = OpenAI(model="gpt-4o")

    def process_event_urls(self, urls: List[str]) -> Optional[Event]:
        """Process a list of URLs that belong to the same event"""
        # Scrape each URL
        contents = []
        for url in urls:
            content = self.scraping_service.scrape(url)
            if content:
                contents.append({"url": url, "content": content})

        if not contents:
            logger.error("Failed to scrape any URLs")
            return None

        # Create a tool for the LLM to scrape additional pages if needed
        scrape_tool = FunctionTool.from_defaults(fn=self.scraping_service.scrape)
        agent = ReActAgent.from_tools([scrape_tool], max_iterations=10, llm=self.llm, verbose=True)

        # Extract event information using LLM
        prompt = f"""Analyze these pages about an open water swimming event.
Visit the following URLs to gather information about a swim event: {', '.join(urls)}
These URLs contain details about the same event. Please analyze all pages and combine the information to create a complete event profile.
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

    def _save_event_data(self, data: Dict, urls: List[str]) -> Event:
        """Save the processed event data to the database"""
        # Create or get Location
        location_data = data["event"]["location"]
        location = self._get_or_create_location(location_data)

        # Get or create organizer
        organizer = self._get_or_create_organizer(data["event"].get("organizer", {}).get("name", ""))

        # Create Event
        event_data = data["event"]
        event = Event.objects.create(
            name=event_data["name"],
            website=event_data.get("website", urls[0]),  # Use the first URL as default
            slug=slugify(event_data["name"]),  # Generate slug from name
            location=location,
            organizer=organizer,
            needs_medical_certificate=event_data.get("needs_medical_certificate"),
            needs_license=event_data.get("needs_license"),
            sold_out=event_data.get("sold_out"),
            cancelled=event_data.get("cancelled"),
            with_ranking=event_data.get("with_ranking"),
            date_start=event_data["date_start"],
            date_end=event_data["date_end"],
            water_temp=event_data.get("water_temp"),
            description=event_data.get("description", ""),
        )

        # Create Races
        for race_data in data["races"]:
            Race.objects.create(
                event=event,
                name=race_data["name"],
                date=race_data["date"],
                race_time=race_data.get("race_time"),
                distance=race_data["distance"],
                wetsuit=race_data.get("wetsuit"),
                price=race_data.get("price", {}).get("amount"),
            )

        return event

    def _get_or_create_location(self, location_data: Dict) -> Optional[Location]:
        """Get or create a location from the provided data"""
        if not location_data.get("city") or not location_data.get("country"):
            return None

        # Convert country name to code
        country = pycountry.countries.get(name=location_data["country"])
        if not country:
            print(f"Could not find country code for {location_data['country']}")
            return None
        country_code = country.alpha_2

        # Try to find an exact match first using all available fields
        location = Location.objects.filter(
            city=location_data["city"],
            country=country_code,
            water_name=location_data.get("water_name"),
            water_type=location_data.get("water_type")
        ).first()

        if location:
            # Update address if provided and different
            if location_data.get("address") and location.address != location_data["address"]:
                location.address = location_data["address"]
                location.save()
            return location

        # If no exact match, create new location
        return Location.objects.create(
            city=location_data["city"],
            country=country_code,
            water_name=location_data.get("water_name"),
            water_type=location_data.get("water_type"),
            address=location_data.get("address")
        )

    def _get_or_create_organizer(self, organizer_name: str) -> Optional[Organizer]:
        """Get or create an organizer using fuzzy matching"""
        if not organizer_name:
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
            return existing_organizers.get(name=best_match[0])
        else:
            # If no good match found, create new organizer
            return Organizer.objects.create(name=organizer_name)
