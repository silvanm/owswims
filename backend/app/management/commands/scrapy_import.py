import json
from collections import OrderedDict
from typing import List, Dict

from django.conf import settings
import googlemaps
import dateparser
import math
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


def deg2rad(deg):
    return deg / 360 * 2 * math.pi


def get_distance_from_lat_lng_in_km(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    d_lat = deg2rad(lat2 - lat1)  # deg2rad below
    d_lon = deg2rad(lon2 - lon1)
    a = \
        math.sin(d_lat / 2) * math.sin(d_lat / 2) + \
        math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * \
        math.sin(d_lon / 2) * math.sin(d_lon / 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c  # Distance in km
    return d


def get_existing_locations_by_lat_lng(lat: float, lng: float) -> List[Dict[str, any]]:
    existing_locations = Location.objects.filter(
        lat__gte=lat - 0.003,
        lat__lte=lat + 0.003,
        lng__gte=lng - 0.02,
        lng__lte=lng + 0.02
    )
    locs = {}
    distances = {}

    for loc in existing_locations:
        dist = get_distance_from_lat_lng_in_km(lat, lng, loc.lat, loc.lng)
        locs[loc.id] = {
            'dist': dist,
            'loc': loc
        }

    locs_sorted = [v for k, v in sorted(locs.items(), key=lambda item: item[1]['dist'])]
    return locs_sorted


class Command(BaseCommand):
    help = "Import events from scrapy and does Geocoding."

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to the json file")
        parser.add_argument("source", help="Source string to use")

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Imports events in the following format:

            {
              "wetsuit": "Wetsuit Optional",
              "water_type": "Lake Swim",
              "name": "Keswick Mountain Festival Derwent Swims",
              "date_start": "2021-05-22 00:00:00",
              "races": [
                1.5,
                3.0
              ],
              "website": "http://keswickmountainfestival.co.uk",
              "description": "5k Open Water Swim; Derwent Island 1500m Swim; Derwentwater 3km Open Water Swim; keswickmountainfestival.co.uk",
              "location": "Crow Park,Keswick,Cumbria UK",
              "source": "championnat de france"
            },

        :param args:
        :param options:
        :return:
        """

        self.gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        with open(options["path"], "r") as fp:
            source_events = json.load(fp)
            for source_event in source_events:
                self.stdout.write(source_event["name"])

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
                    e.location = location
                    e.save()

                    if "races" in source_event:
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

                    self.stdout.write(self.style.SUCCESS(f"Event {source_event['name']} saved."))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f"Event {source_event['name']} exists already. Not saving."
                    ))

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

            location.address = geocoded_address["route"]
            if geocoded_address["street_number"]:
                location.address += geocoded_address["street_number"]

            location.city = (
                geocoded_address["locality"]
                if geocoded_address["locality"]
                else geocoded_address["postal_town"]
            )
            location.country = geocoded_address["country"]
            location.lat = geocode_result[0]["geometry"]["location"]["lat"]
            location.lng = geocode_result[0]["geometry"]["location"]["lng"]

            location.address += f', {location.city}, {location.country}'

            if "water_type" in source_event:
                location.water_type = WATER_TYPE_MAP[source_event["water_type"]]

            # See if there are locations close-by, then let's use those locations
            existing_locations = get_existing_locations_by_lat_lng(lat=location.lat, lng=location.lng)

            if len(existing_locations) > 0:
                self.stderr.write(
                    self.style.SUCCESS(
                        f"Location {source_event['location']} "
                        f"exists already. Not saving"
                    )
                )
                return existing_locations[0]['loc']
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
