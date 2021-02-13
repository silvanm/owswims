from django.core.validators import MinLengthValidator

from app.importer.traversate import import_traversate, ImportResult
import logging

from . import models
from .models import Location, Event, Race


def import_events():
    events = import_traversate()
    Location.objects.all().delete()
    Event.objects.all().delete()
    for event in events["parsed_items"]:
        (location_model, created) = Location.objects.get_or_create(
            city=event["location"][0],
            country=event["location"][1],
        )
        # print(
        #    f'Searching city={event["location"][0]}, country={event["location"][1]}. '
        #    f"Created: {created}. Id: {location_model.id}"
        # )
        event_model = Event.objects.create(
            location=location_model,
            name=event["event"],
            date_start=event["dates"][0],
            date_end=event["dates"][1],
            website=event["website"]
        )
        for race in event["races"]:
            Race.objects.create(event=event_model, date=event["dates"][0], distance=race)
    logging.info(f"Imported items: {len(events['parsed_items'])}")
    logging.warning(f"Failed items: {len(events['failed_items'])}")

    print(events['failed_items'])


class EventChecker():
    event_share = 0.5
    event_fields = [
        {'name': 'website', 'points': 5},
        {'name': 'flyer_image', 'points': 5},
        {'name': 'location', 'points': 10},
        {'name': 'organizer', 'points': 2},
        {'name': 'needs_medical_certificate', 'points': 1},
        {'name': 'needs_license', 'points': 1},
        {'name': 'with_ranking', 'points': 1},
        {'name': 'water_temp', 'points': 1},
        {'name': 'description', 'points': 5},
    ]

    race_share = 0.3
    race_fields = [
        {'name': 'distance', 'points': 10},
        {'name': 'name', 'points': 5},
        {'name': 'wetsuit', 'points': 2},
        {'name': 'price', 'points': 2},
        {'name': 'coordinates', 'points': 20},
    ]

    location_share = 0.3
    location_fields = [
        {'name': 'city', 'points': 10},
        {'name': 'country', 'points': 10},
        {'name': 'lat', 'points': 10},
        {'name': 'lng', 'points': 10},
        {'name': 'header_photo', 'points': 10},
    ]

    def __init__(self, event: models.Event):
        self.event = event

    def _rate_event(self, event: models.Event) -> int:
        points = 0
        for field_data in self.event_fields:
            if getattr(event, field_data['name']):
                points += field_data['points']
        return points

    def _rate_location(self, location: models.Location) -> int:
        points = 0
        for field_data in self.location_fields:
            if getattr(location, field_data['name']):
                points += field_data['points']
        return points

    def _rate_race(self, race: models.Race) -> int:
        points = 0
        for field_data in self.race_fields:
            if getattr(race, field_data['name']):
                points += field_data['points']
        return points

    def get_rating(self):
        """
        Rate entry quality according to checks
        :return:
        """
        points = self.event_share * self._rate_event(self.event) \
                 + self.location_share * self._rate_location(self.event.location)

        race_points = [self._rate_race(r) for r in self.event.races.all()]
        if len(race_points) == 0:
            return int(points)
        else:
            return int(points + self.race_share * sum(race_points) / len(race_points))
