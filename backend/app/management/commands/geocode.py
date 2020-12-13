import googlemaps
from django.conf import settings
from django.core.management.base import BaseCommand

from app.models import Location


class Command(BaseCommand):
    help = "Geocodes the locations which are not geocoded yet"

    def handle(self, *args, **options):
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

        for location in Location.objects.filter(lat__isnull=True):
            geocode_result = gmaps.geocode(f"{location.city}, {location.country.name}")
            if geocode_result:
                location.lat = geocode_result[0]["geometry"]["location"]["lat"]
                location.lng = geocode_result[0]["geometry"]["location"]["lng"]
                location.save()
                self.stderr.write(
                    self.style.WARNING(f"Geocoding {repr(location)} successful.")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Geocoding {repr(location)} failed.")
                )
