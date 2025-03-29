from django.core.management.base import BaseCommand

from app.models import Location
from app.services import GeocodingService


class Command(BaseCommand):
    help = "Geocodes the locations which are not geocoded yet"

    def handle(self, *args, **options):
        # Initialize the geocoding service
        geocoding_service = GeocodingService(stdout=self.stdout, stderr=self.stderr)

        # Get all locations without coordinates
        locations = Location.objects.filter(lat__isnull=True)
        self.stdout.write(f"Found {locations.count()} locations to geocode")

        # Process each location
        for location in locations:
            self.stdout.write(f"Geocoding {location}...")

            # Use the geocoding service to geocode the location
            success = geocoding_service.geocode_location(location)

            if success:
                location.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Geocoding {location} successful.")
                )
            else:
                self.stdout.write(self.style.ERROR(f"Geocoding {location} failed."))
