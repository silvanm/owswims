from datetime import date

from django.core.management.base import BaseCommand

from app.models import Event, Review


class Command(BaseCommand):
    help = "Copy the events to the next year"

    def add_arguments(self, parser):
        parser.add_argument("target_year", help="Year to copy the events to")

    def handle(self, *args, **options):
        # find all events of this year which are visible and approved
        target_year = int(options['target_year'])
        events = Event.objects.filter(date_start__gte=date(target_year - 1, 1, 1),
                                      date_start__lt=date(target_year, 1, 1),
                                      verified_at__isnull=False, invisible__isnull=False)
        self.stdout.write(f"Copying {len(events)} events")

        for event in events:
            self.stdout.write(f"Copying {event}")
            event_copy: Event = event.make_clone()

            # change dates to target_year
            event_copy.date_start = event_copy.date_start.replace(year=target_year)
            event_copy.date_end = event_copy.date_end.replace(year=target_year)
            for race in event_copy.races.all():
                race.date = event_copy.date_start.replace(year=target_year)
                race.save()

            # set invisible and unverified
            event_copy.verified_at = None
            event_copy.invisible = True
            # link with previous year
            event_copy.previous_year_event = event

            event_copy.source = 'Copied from past year'

            # copy comments from past year
            for review in event.reviews.all():
                review_copy: Review = review.make_clone()
                review_copy.event = event_copy
                review_copy.created_at = review.created_at
                review_copy.save()

            event_copy.save()
