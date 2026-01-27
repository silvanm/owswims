import csv
from datetime import date

from django.core.management.base import BaseCommand

from app.models import Event


class Command(BaseCommand):
    help = "Export events with race details to CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=date.today().year,
            help="Year to export events for (default: current year)",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="events_export.csv",
            help="Output CSV file path",
        )
        parser.add_argument(
            "--country",
            type=str,
            help="Filter by country code (e.g., CH, DE)",
        )

    def handle(self, *args, **options):
        year = options["year"]
        output_file = options["output"]
        country = options.get("country")

        self.stdout.write(f"Exporting events for {year}...")

        # Get events for the specified year
        events = Event.objects.filter(
            date_start__year=year,
            invisible=False,
        )

        if country:
            events = events.filter(location__country=country)

        events = events.order_by("date_start")

        self.stdout.write(f"Found {events.count()} events")

        rows = []
        for event in events:
            # Get all races for this event
            races = event.race_set.all()

            # Calculate race statistics
            distances = [r.distance for r in races if r.distance]
            min_distance = min(distances) if distances else None
            max_distance = max(distances) if distances else None
            race_count = len(list(races))

            # Build race details string
            race_details = "; ".join(
                [f"{r.name or 'Race'}: {r.distance}m" for r in races if r.distance]
            )

            rows.append({
                "id": event.id,
                "name": event.name,
                "date": event.date_start,
                "location": event.location.name if event.location else "",
                "country": event.location.country if event.location else "",
                "organizer": event.organizer.name if event.organizer else "",
                "website": event.website or "",
                "race_count": race_count,
                "min_distance_m": min_distance,
                "max_distance_m": max_distance,
                "race_details": race_details,
                "cancelled": event.cancelled,
                "sold_out": event.sold_out,
            })

        # Write to CSV
        if rows:
            fieldnames = rows[0].keys()
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            self.stdout.write(
                self.style.SUCCESS(f"Exported {len(rows)} events to {output_file}")
            )
        else:
            self.stdout.write(self.style.WARNING("No events found to export"))
