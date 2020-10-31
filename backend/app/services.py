from app.importer.traversate import import_traversate, ImportResult
import logging

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
        #print(
        #    f'Searching city={event["location"][0]}, country={event["location"][1]}. '
        #    f"Created: {created}. Id: {location_model.id}"
        #)
        event_model = Event.objects.create(
            location=location_model,
            name=event["event"],
            date_start=event["dates"][0],
            date_end=event["dates"][1],
        )
        for race in event["races"]:
            Race.objects.create(event=event_model, date=event["dates"][0], distance=race)
    logging.info(f"Imported items: {len(events['parsed_items'])}")
    logging.warning(f"Failed items: {len(events['failed_items'])}")

    print(events['failed_items'])
