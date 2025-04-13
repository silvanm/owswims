from django.core.management.base import BaseCommand
from django.db.models import Count
from app.models import Event, Location
import click
from datetime import datetime
from typing import List, Dict, Tuple
from django.utils import timezone


def find_duplicate_events(location_id=None) -> Dict[Tuple[int, datetime], List[Event]]:
    """
    Find events that are at the same location on the same date

    If location_id is provided, only check duplicates at that location
    Returns a dictionary with (location_id, date) as key and a list of duplicate events as value
    Only considers future events.
    """
    current_date = timezone.now().date()
    events = Event.objects.filter(date_start__gte=current_date)

    if location_id:
        events = events.filter(location_id=location_id)

    # Group events by location and date
    duplicates = {}
    for event in events:
        key = (event.location_id, event.date_start)
        if key not in duplicates:
            duplicates[key] = []
        duplicates[key].append(event)

    # Filter out entries with only one event
    return {k: v for k, v in duplicates.items() if len(v) > 1}


def print_event_info(event: Event) -> str:
    """Format event information for display"""
    return (
        f"ID: {event.id}\n"
        f"Name: {event.name}\n"
        f"Date: {event.date_start} to {event.date_end}\n"
        f"Organizer: {event.organizer.name if event.organizer else 'N/A'}\n"
        f"Number of Races: {event.races.count()}\n"
        f"Races: {', '.join([f'{race.distance}km on {race.date}' for race in event.races.all()])}\n"
        f"Verified: {'Yes' if event.is_verified() else 'No'}\n"
        f"Has Image: {'Yes' if event.flyer_image else 'No'}\n"
        f"Internal Comment: {event.internal_comment or 'N/A'}\n"
        f"Created By: {event.created_by or 'N/A'}\n"
        f"Created At: {event.created_at}\n"
        "---"
    )


class Command(BaseCommand):
    help = """
    Find and handle duplicate events at the same location on the same date.
    
    This command identifies future events in the database that are at the same location
    on the same date and allows you to choose which one to keep and which ones to delete.
    The command will:
    
    1. Find all future events that are at the same location on the same date
    2. For each group of duplicate events, display information about each event
    3. Recommend a default event to keep (the one with the most races)
    4. Allow you to choose which event to keep (with the recommended default pre-selected)
    5. Delete all other events (races associated with deleted events will also be deleted)
    
    Note: Only future events (with start date >= current date) are considered.
    
    Use the --dry-run option to see what would be processed without making any changes.
    Use the --location option to only check for duplicates at a specific location.
    Use the --limit option to process only a specific number of duplicate groups.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--location",
            type=int,
            help="Check for duplicates only at this location ID",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be processed without making any changes",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of duplicate groups to process",
        )

    def handle(self, *args, **options):
        location_id = options["location"]
        dry_run = options["dry_run"]
        limit = options["limit"]

        current_date = timezone.now().date()
        self.stdout.write(
            f"Searching for duplicate future events (start date >= {current_date})..."
        )
        if location_id:
            try:
                location = Location.objects.get(id=location_id)
                self.stdout.write(f"Limiting search to location: {location}")
            except Location.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Location with ID {location_id} does not exist")
                )
                return

        duplicate_groups = find_duplicate_events(location_id)

        if not duplicate_groups:
            self.stdout.write(self.style.SUCCESS("No duplicate events found."))
            return

        # Limit the number of groups to process if requested
        if limit is not None:
            keys = list(duplicate_groups.keys())[:limit]
            duplicate_groups = {k: duplicate_groups[k] for k in keys}
            self.stdout.write(
                f"Processing {len(duplicate_groups)} groups of duplicate events (limited by --limit option)."
            )
        else:
            self.stdout.write(
                f"Found {len(duplicate_groups)} groups of duplicate events."
            )

        total_events_to_delete = sum(
            len(events) - 1 for events in duplicate_groups.values()
        )
        self.stdout.write(
            f"Total events that will be deleted: {total_events_to_delete}"
        )
        self.stdout.write(f"Total events that will remain: {len(duplicate_groups)}")
        self.stdout.write("=" * 50)

        for (location_id, date), events in duplicate_groups.items():
            location = Location.objects.get(id=location_id)
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(f"Duplicate events at {location} on {date}:")

            # Display each event
            for i, event in enumerate(events, 1):
                self.stdout.write(f"\nEvent {i}:")
                self.stdout.write(print_event_info(event))

            if not dry_run:
                # Sort events by number of races (descending) to determine the default choice
                events_with_index = [
                    (i, event, event.races.count()) for i, event in enumerate(events, 1)
                ]
                events_with_index.sort(
                    key=lambda x: x[2], reverse=True
                )  # Sort by race count (descending)

                # Default choice is the first event in the sorted list (most races)
                default_choice = events_with_index[0][0]

                # Display recommendation
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nRecommended choice: Event {default_choice} ({events[default_choice-1].name}) with {events_with_index[0][2]} races"
                    )
                )

                # Ask user which event to keep
                choices = list(range(1, len(events) + 1))
                choice = None

                while choice not in choices:
                    choice_str = click.prompt(
                        "\nWhich event would you like to keep? (enter number)",
                        type=str,
                        default=str(default_choice),
                    )
                    try:
                        choice = int(choice_str)
                        if choice not in choices:
                            self.stdout.write(
                                self.style.ERROR(
                                    f"Please enter a number between 1 and {len(events)}"
                                )
                            )
                    except ValueError:
                        self.stdout.write(
                            self.style.ERROR("Please enter a valid number")
                        )

                keep_event = events[choice - 1]
                delete_events = [e for i, e in enumerate(events) if i != choice - 1]

                if click.confirm(
                    f"\nKeeping event {choice} ({keep_event.name}). Delete {len(delete_events)} other events?",
                    default=True,
                ):
                    # Delete all other events
                    deleted_race_count = 0
                    for event in delete_events:
                        # Count races before deleting them
                        deleted_race_count += event.races.count()
                        # Delete all races associated with the event
                        event.races.all().delete()
                        # Delete the event
                        event.delete()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Events deleted successfully. {len(delete_events)} events and {deleted_race_count} races were deleted."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("Skipping this group of events.")
                    )
            else:
                self.stdout.write(self.style.WARNING("Dry run - no changes made."))
