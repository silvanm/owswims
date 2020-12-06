import json
from django.conf import settings
import googlemaps
import dateparser
from django.db import transaction

from app.models import Location, Event, Race

from django.core.management.base import BaseCommand

WATER_TYPE_MAP = {
    "Lake Swim": "lake",
    "Sea Swim": "sea",
    "River Swim": "river",
    "Estuary Swim": "sea",
    "Other": None,
}

WETSUIT_MAP = {
    "Wetsuit Optional": "optional",
    "Wetsuit Compulsory": "compulsory",
    "Wetsuit Prohibited": "prohibited",
}


class Command(BaseCommand):
    help = "Import events from scrapy and does Geocoding."

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to the json file")
        parser.add_argument("source", help="Source string to use")

    @transaction.atomic
    def handle(self, *args, **options):
        self.gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)
        with open(options["path"], "r") as fp:
            source_events = json.load(fp)
            for source_event in source_events:
                self.stdout.write(source_event["name"])

                # Ignore events with no races
                if "races" not in source_event:
                    self.style.SUCCESS(f"Event {source_event['name']} has no races.")
                    continue

                location = self.process_location(source_event)

                date = dateparser.parse(source_event["date_start"])
                num_events = Event.objects.filter(
                    date_start=date, name=source_event["name"]
                ).count()
                if num_events == 0:
                    e = Event()
                    e.source = options["source"]
                    e.date_start = date
                    e.date_end = date
                    e.name = source_event["name"]
                    if "website" in source_event:
                        e.website = source_event["website"]
                    e.description = (
                        source_event["description"]
                        if "description" in source_event
                        else ""
                    )
                    if "water_type" in source_event:
                        e.water_type = WATER_TYPE_MAP[source_event["water_type"]]
                    e.location = location
                    e.save()

                    for dist in source_event["races"]:
                        r = Race(
                            date=e.date_start,
                            distance=dist,
                            wetsuit=WETSUIT_MAP[source_event["wetsuit"]]
                            if "wetsuit" in source_event
                            else None,
                            event=e,
                        )
                        r.save()

                    self.style.SUCCESS(f"Event {source_event['name']} saved.")
                else:
                    self.style.SUCCESS(
                        f"Event {source_event['name']} exists already. Not saving."
                    )

    def process_location(self, source_event) -> Location:
        geocode_result = self.gmaps.geocode(source_event["location"])
        location = Location()
        if geocode_result:
            geocoded_address = {
                "street_number": "",
                "route": "",
                "locality": "",
                "postal_town": "",
                "country": "",
            }

            for component in geocode_result[0]["address_components"]:
                for part in geocoded_address.keys():
                    if part in component["types"]:
                        geocoded_address[part] = (
                            component["long_name"]
                            if part != "country"
                            else component["short_name"]
                        )

            location.street = geocoded_address["route"]
            if geocoded_address["street_number"]:
                location.street += geocoded_address["street_number"]
            location.city = (
                geocoded_address["locality"]
                if geocoded_address["locality"]
                else geocoded_address["postal_town"]
            )
            location.country = geocoded_address["country"]
            location.lat = geocode_result[0]["geometry"]["location"]["lat"]
            location.lng = geocode_result[0]["geometry"]["location"]["lng"]

            existing_locations = Location.objects.filter(
                lat=location.lat, lng=location.lng
            )

            if len(existing_locations) > 0:
                self.stderr.write(
                    self.style.SUCCESS(
                        f"Location {source_event['location']} "
                        f"exists already. Not saving"
                    )
                )
                return existing_locations[0]
            else:
                location.save()
                self.stderr.write(
                    self.style.SUCCESS(
                        f"Geocoding {source_event['location']} successful."
                    )
                )
                return location
        else:
            self.stdout.write(
                self.style.WARNING(f"Geocoding {source_event['location']} failed.")
            )
