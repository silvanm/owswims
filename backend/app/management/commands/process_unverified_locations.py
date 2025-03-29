import logging
import os
import uuid
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from app.models import Location
from app.services import GeocodingService

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
        # Initialize the geocoding service
        self.geocoding_service = GeocodingService(
            stdout=self.stdout, stderr=self.stderr
        )

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
            self.stdout.write(
                self.style.WARNING(
                    f"⚠ Location {location.id} has no address, skipping geocoding"
                )
            )
        else:
            # Geocode the location if needed
            if not location.lat or not location.lng:
                geocoded = self.geocoding_service.geocode_location(location)
                if geocoded:
                    location.save(update_fields=["lat", "lng", "address"])
            else:
                geocoded = True
                self.stdout.write(f"ℹ Location already has coordinates")

        # Get header image if needed
        if not location.header_photo:
            image_added = self.fetch_and_set_header_image(location)
        else:
            image_added = True
            self.stdout.write(f"ℹ Location already has a header image")

        return geocoded and image_added

    def fetch_and_set_header_image(self, location):
        """Fetch and set a header image for the location using Google Places API"""
        try:
            self.stdout.write(f"ℹ Fetching images for location")

            # Skip if no coordinates
            if not location.lat or not location.lng:
                self.stdout.write(
                    self.style.WARNING(f"⚠ Cannot fetch images without coordinates")
                )
                return False

            # Find a place using the geocoding service
            place_details = self.geocoding_service.find_place_by_location(location)

            if not place_details:
                self.stdout.write(
                    self.style.WARNING(f"⚠ No suitable place found for this location")
                )
                return False

            # Check if the place has photos
            if "photos" not in place_details or not place_details["photos"]:
                self.stdout.write(self.style.WARNING(f"⚠ No photos found for place"))
                return False

            # Get the first photo
            photo_reference = place_details["photos"][0]["photo_reference"]
            photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={settings.GOOGLE_MAPS_API_KEY}"

            # Download and save the image
            with requests.get(photo_url, stream=True) as r:
                if r.status_code != 200:
                    self.stdout.write(
                        self.style.ERROR(
                            f"✗ Failed to download image: HTTP {r.status_code}"
                        )
                    )
                    return False

                r.raw.seek = lambda x, y: 0
                r.raw.size = int(r.headers.get("Content-Length", 0))
                filename = f"location_{location.id}_{uuid.uuid4().hex[:8]}.jpeg"

                # Save the image
                location.header_photo.save(filename, r.raw, save=True)
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Successfully saved header image: {filename}")
                )
                return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Image fetching error: {str(e)}"))
            return False
