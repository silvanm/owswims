import logging
import os
import uuid
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import googlemaps
from app.models import Location

# Configure logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Process unverified locations to add coordinates and header images"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, help="Limit the number of locations to process"
        )
        parser.add_argument(
            "--auto-verify",
            action="store_true",
            help="Automatically mark locations as verified after processing",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be processed without making changes",
        )

    def handle(self, *args, **options):
        # Get unverified locations
        locations = Location.objects.filter(verified_at__isnull=True)

        if options["limit"]:
            locations = locations[: options["limit"]]

        count = locations.count()
        self.stdout.write(f"Found {count} unverified locations to process")

        if options["dry_run"]:
            for location in locations:
                self.stdout.write(f"Would process: {location}")
            return

        processed = 0
        for i, location in enumerate(locations):
            self.stdout.write(f"Processing {i+1}/{count}: {location}")

            # Process the location
            updated = self.process_location(location)

            # Auto-verify if requested and successfully processed
            if options["auto_verify"] and updated:
                location.verified_at = timezone.now()
                location.save(update_fields=["verified_at"])
                self.stdout.write(self.style.SUCCESS(f"  ✓ Verified"))
                processed += 1

            # Report status
            if updated:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Successfully processed"))
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠ Processing incomplete"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished processing {processed} out of {count} locations"
            )
        )

    def process_location(self, location):
        """
        Process an unverified location to add coordinates and header image
        Returns True if processing was successful
        """
        success = False
        geocoded = False
        image_added = False

        # Skip if no address
        if not location.address:
            print(f"⚠ Location {location.id} has no address, skipping geocoding")
        else:
            # Geocode the location if needed
            if not location.lat or not location.lng:
                geocoded = self.geocode_location(location)
            else:
                geocoded = True
                print(f"ℹ Location already has coordinates")

        # Get header image if needed
        if not location.header_photo:
            image_added = self.fetch_and_set_header_image(location)
        else:
            image_added = True
            print(f"ℹ Location already has a header image")

        return geocoded and image_added

    def geocode_location(self, location):
        """Geocode a location using its address"""
        try:
            print(f"ℹ Geocoding address: {location.address}")

            # Initialize Google Maps client
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

            # Get country name from country code
            import pycountry

            country = pycountry.countries.get(alpha_2=location.country.code)
            country_name = country.name if country else ""

            # Use the full address for geocoding
            geocode_query = f"{location.address}, {country_name}"
            geocode_result = gmaps.geocode(geocode_query)

            if geocode_result:
                location.lat = geocode_result[0]["geometry"]["location"]["lat"]
                location.lng = geocode_result[0]["geometry"]["location"]["lng"]
                location.save(update_fields=["lat", "lng"])
                print(f"✓ Successfully geocoded: {location.lat}, {location.lng}")
                return True
            else:
                print(f"✗ No geocoding results for: {geocode_query}")
                return False

        except Exception as e:
            print(f"✗ Geocoding error: {str(e)}")
            return False

    def fetch_and_set_header_image(self, location):
        """Fetch and set a header image for the location using Google Places API"""
        try:
            print(f"ℹ Fetching images for location")

            # Skip if no coordinates
            if not location.lat or not location.lng:
                print(f"⚠ Cannot fetch images without coordinates")
                return False

            # Initialize Google Maps client
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

            # Try different search strategies
            place_id = None
            place_details = None

            # Strategy 1: Find place from address (matching frontend behavior)
            if location.address:
                print(f"ℹ Searching for place using address: {location.address}")

                # Use findplacefromtext to search by address (similar to Places Autocomplete)
                try:
                    find_place_result = gmaps.find_place(
                        input=location.address,
                        input_type="textquery",
                        fields=["place_id", "name", "formatted_address"],
                        location_bias="circle:5000@{},{}".format(
                            location.lat, location.lng
                        ),
                    )
                except Exception as e:
                    print(f"⚠ Error in find_place: {str(e)}")
                    find_place_result = {"candidates": []}

                if find_place_result.get("candidates"):
                    place_id = find_place_result["candidates"][0]["place_id"]
                    place_name = find_place_result["candidates"][0].get(
                        "name", "Unknown"
                    )
                    print(f"✓ Found place from address: {place_name}")

            # Strategy 2: Text Search by address if find_place didn't work
            if not place_id and location.address:
                print(f"ℹ Trying text search with address")

                text_search_result = gmaps.places(
                    query=location.address,
                    location=(location.lat, location.lng),
                    radius=5000,  # 5km radius
                )

                if text_search_result.get("results"):
                    place_id = text_search_result["results"][0]["place_id"]
                    print(
                        f"✓ Found place via text search: {text_search_result['results'][0].get('name', 'Unknown')}"
                    )

            # Strategy 3: Nearby Search as fallback
            if not place_id:
                print(f"ℹ Trying nearby search for relevant places")

                # Determine place types based on water type
                place_types = ["natural_feature", "point_of_interest"]
                if location.water_type:
                    if location.water_type == "sea":
                        place_types = ["natural_feature", "beach"]
                    elif location.water_type == "lake":
                        place_types = ["natural_feature", "lake"]
                    elif location.water_type == "river":
                        place_types = ["natural_feature", "river"]
                    elif location.water_type == "pool":
                        place_types = ["swimming_pool"]

                # Try each place type
                for place_type in place_types:
                    nearby_search_result = gmaps.places_nearby(
                        location=(location.lat, location.lng),
                        radius=2000,  # 2km radius
                        type=place_type,
                    )

                    if nearby_search_result.get("results"):
                        place_id = nearby_search_result["results"][0]["place_id"]
                        print(
                            f"✓ Found place via nearby search: {nearby_search_result['results'][0].get('name', 'Unknown')}"
                        )
                        break

            # If we found a place, get its details
            if place_id:
                place_details = gmaps.place(
                    place_id=place_id,
                    fields=["name", "photo", "formatted_address", "type", "geometry"],
                )

                # Log place details for debugging
                place_name = place_details["result"].get("name", "Unknown")
                place_address = place_details["result"].get(
                    "formatted_address", "Unknown"
                )
                place_types = place_details["result"].get("types", [])
                print(
                    f"ℹ Place details - Name: {place_name}, Address: {place_address}, Types: {', '.join(place_types[:3])}"
                )

                # Update lat/lng from the identified place
                if (
                    "geometry" in place_details["result"]
                    and "location" in place_details["result"]["geometry"]
                ):
                    place_lat = place_details["result"]["geometry"]["location"]["lat"]
                    place_lng = place_details["result"]["geometry"]["location"]["lng"]

                    # Only update if the coordinates are significantly different
                    lat_diff = abs(place_lat - location.lat)
                    lng_diff = abs(place_lng - location.lng)

                    if (
                        lat_diff > 0.0001 or lng_diff > 0.0001
                    ):  # About 10 meters difference
                        print(
                            f"ℹ Updating coordinates from place: {place_lat}, {place_lng}"
                        )
                        print(f"ℹ Previous coordinates: {location.lat}, {location.lng}")
                        location.lat = place_lat
                        location.lng = place_lng
                        location.save(update_fields=["lat", "lng"])
            else:
                print(f"⚠ No suitable place found for this location")
                return False

            # Check if the place has photos
            if (
                "photos" not in place_details["result"]
                or not place_details["result"]["photos"]
            ):
                print(f"⚠ No photos found for place")
                return False

            # Get the first photo
            photo_reference = place_details["result"]["photos"][0]["photo_reference"]
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={settings.GOOGLE_MAPS_API_KEY}"

            # Download and save the image
            with requests.get(photo_url, stream=True) as r:
                if r.status_code != 200:
                    print(f"✗ Failed to download image: HTTP {r.status_code}")
                    return False

                r.raw.seek = lambda x, y: 0
                r.raw.size = int(r.headers.get("Content-Length", 0))
                filename = f"location_{location.id}_{uuid.uuid4().hex[:8]}.jpeg"

                # Save the image
                location.header_photo.save(filename, r.raw, save=True)
                print(f"✓ Successfully saved header image: {filename}")
                return True

        except Exception as e:
            print(f"✗ Image fetching error: {str(e)}")
            return False
