# this is deprecated and replaced by crawl_events
import datetime
import os
import json
import re
from django.core.management.base import BaseCommand
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
import dotenv
from firecrawl import FirecrawlApp
from app.models import Event, Location, Organizer, Race
import pycountry
from thefuzz import fuzz, process
from django.utils.text import slugify

dotenv.load_dotenv()


class Command(BaseCommand):
    help = "Scrapes websites using Firecrawl and processes them with LLM"

    def add_arguments(self, parser):
        parser.add_argument("urls", nargs="+", type=str, help="URLs to scrape")
        parser.add_argument(
            "--output",
            default="response",
            help="Base name for the output file (default: response)",
        )

    def handle(self, *args, **options):
        self.main(options["urls"], options["output"])

    def main(self, urls, output_base):
        firecrawl_app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])

        def scrape(url: str) -> str:
            """Scrape a webpage and return the content"""
            scrape_result = firecrawl_app.scrape_url(
                url,
                params={
                    "formats": ["markdown"],
                    "excludeTags": ["script", "style", "svg", "iframe"],
                    "waitFor": 1000,
                },
            )
            return scrape_result["markdown"]

        scrape_tool = FunctionTool.from_defaults(fn=scrape)

        llm = OpenAI(model="gpt-4o")
        agent = ReActAgent.from_tools(
            [scrape_tool], max_iterations=10, llm=llm, verbose=True
        )

        prompt = f"""Visit the following URLs to gather information about a swim event: {', '.join(urls)}
These URLs contain details about the same event. Please analyze all pages and combine the information to create a complete event profile.
Return the information as JSON. The response should be in the following format:
{{
    "event": {{
        "name": "Summer Swim Marathon",  // The name of the event (Event.name)
        "website": "https://summerswimmarathon.com/race/summer-swim-marathon",  // The event's official website. Note that if this is an event serie, 
                                      // then this should point to the events website, not the website of the serie (Event.website)
        "flyer_image": "https://summerswimmarathon.com/flyer.jpg",  // URL to the event's flyer image (Event.flyer_image)
        "location": {{
            "city": "Zurich",  // The city where the event is located (Location.city)
            "water_name": "Lake Zurich",  // Name of the body of water (Location.water_name)
            "water_type": "lake",  // Type of water body (river, sea, lake, pool) (Location.water_type)
            "country": "Switzerland",  // Country where the event is held (Location.country)
            "address": "Seestrasse 123, Zurich, Switzerland",  // Detailed address (Location.address)              
        }},
        "organizer": {{
            "name": "Swiss Open Water Association",  // Name of the event organizer (Organizer.name)              
        }},
        "needs_medical_certificate": true,  // Indicates if a medical certificate is required (Event.needs_medical_certificate)
        "needs_license": false,  // Indicates if a racing license is required (Event.needs_license)
        "sold_out": false,  // If the event is sold out (Event.sold_out)
        "cancelled": false,  // If the event is cancelled (Event.cancelled)
        "with_ranking": true,  // If the event will have a ranking system (Event.with_ranking)
        "date_start": "2024-07-15",  // Start date of the event (Event.date_start)
        "date_end": "2024-07-16",  // End date of the event (Event.date_end)
        "water_temp": 22.5,  // Water temperature in Celsius at the event (Event.water_temp)
        "description": "The Summer Swim Marathon is a challenging event open to professional and amateur swimmers."  
        // Public description of the event. Try to find it on the website URLs I provided (Event.description)
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

        # Write response to file
        timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M")
        filename = f"{output_base}_{timestamp}.txt"

        with open(filename, "w") as f:
            f.write(response.response)

        # Parse the JSON response
        try:
            # Extract JSON from the response
            json_text = response.response
            # Find the JSON content between triple backticks if present
            json_match = re.search(r"```json\s*(.*?)\s*```", json_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)

            data = json.loads(json_text)

            # Create or get Location
            location_data = data["event"]["location"]
            # Convert country name to ISO code
            country_name = location_data["country"]
            try:
                country = pycountry.countries.search_fuzzy(country_name)[0]
                country_code = country.alpha_2
            except:
                self.stdout.write(
                    self.style.WARNING(
                        f"Could not find country code for {country_name}, using XX"
                    )
                )
                country_code = "XX"

            # Check if multiple locations exist
            locations = Location.objects.filter(
                city=location_data["city"], country=country_code
            )

            if locations.count() > 1:
                self.stdout.write(
                    self.style.WARNING(
                        f'Multiple locations found for {location_data["city"]}, {country_code}. Using first match.'
                    )
                )

            # Get first match or create new
            location, _ = Location.objects.get_or_create(
                city=location_data["city"],
                country=country_code,
                defaults={
                    "water_name": location_data.get("water_name"),
                    "water_type": location_data.get("water_type"),
                    "address": location_data.get("address"),
                },
            )

            # Get or create organizer with fuzzy matching

            organizer_name = data["event"].get("organizer", {}).get("name", "")
            if organizer_name:
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
                    organizer = best_match[0][0]  # Get the matched organizer object
                else:
                    # If no good match found, create new organizer
                    organizer = Organizer.objects.create(name=organizer_name)
            else:
                organizer = None

            # Create Event
            event_data = data["event"]
            event = Event.objects.create(
                name=event_data["name"],
                website=event_data.get(
                    "website", urls[0]
                ),  # Use the first URL as default
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
                description=event_data.get(
                    "description", ""
                ),  # Use description from the data, empty string as fallback
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

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully scraped URLs and saved to database. Event ID: {event.id}"
                )
            )
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to parse JSON response: {str(e)}")
            )
            # Print the text that failed to parse for debugging
            self.stdout.write(json_text)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error saving to database: {str(e)}"))
