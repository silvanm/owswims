from django.core.management.base import BaseCommand
from django.db.models import Q
from app.models import Location, Event
from app.services.geocoding_service import GeocodingService
from typing import List, Tuple, Dict
import click


def find_nearby_locations(
    distance_meters: float = 500,
) -> List[Tuple[Location, List[Tuple[Location, float]]]]:
    """
    Find locations that are within the specified distance of each other
    Returns a list of tuples (location_to_keep, [locations_to_merge])
    """
    locations = Location.objects.filter(lat__isnull=False, lng__isnull=False)
    nearby_pairs = []
    processed = set()
    geocoding_service = GeocodingService()

    for loc1 in locations:
        if loc1.id in processed:
            continue

        nearby = []
        for loc2 in locations:
            if loc1.id == loc2.id or loc2.id in processed:
                continue

            distance = (
                geocoding_service.get_distance_from_lat_lng_in_km(
                    loc1.lat, loc1.lng, loc2.lat, loc2.lng
                )
                * 1000
            )  # Convert to meters

            if distance <= distance_meters:
                nearby.append((loc2, distance))
                processed.add(loc2.id)

        if nearby:
            # Add the current location to the group for comparison
            all_locations = [(loc1, 0)] + nearby

            # Sort locations by priority:
            # 1. Is verified
            # 2. Has header_photo
            # 3. Number of events (descending)
            all_locations.sort(
                key=lambda x: (
                    not x[0].is_verified(),  # False (0) comes before True (1)
                    not bool(x[0].header_photo),  # False (0) comes before True (1)
                    x[0].events.count(),  # Lower numbers come first
                )
            )

            # The first location after sorting is the one to keep
            keep_loc, _ = all_locations[0]
            merge_locs = all_locations[1:]

            nearby_pairs.append((keep_loc, merge_locs))
            processed.add(loc1.id)
            processed.update(loc[0].id for loc in merge_locs)

    return nearby_pairs


def print_location_info(location: Location, distance: float = None) -> str:
    """Format location information for display"""
    distance_info = (
        f"Distance from kept location: {distance:.1f}m\n"
        if distance is not None
        else ""
    )
    return (
        f"ID: {location.id}\n"
        f"Name: {location.water_name or 'N/A'}, {location.city}, {location.country}\n"
        f"Coordinates: {location.lat}, {location.lng}\n"
        f"Address: {location.address or 'N/A'}\n"
        f"Water Type: {location.water_type or 'N/A'}\n"
        f"Verified: {'Yes' if location.is_verified() else 'No'}\n"
        f"Has Image: {'Yes' if location.header_photo else 'No'}\n"
        f"Number of Events: {location.events.count()}\n"
        f"{distance_info}"
        "---"
    )


class Command(BaseCommand):
    help = """
    Merge locations that are within a specified distance of each other.
    
    This command identifies duplicate locations within the database that are geographically close
    (within the specified distance) and merges them to consolidate data. The command will:
    
    1. Find all locations with coordinates that are within the specified distance of each other
    2. Prioritize which location to keep based on verification status, presence of images, and number of events
    3. Update all events at the merged locations to point to the kept location
    4. Delete the merged locations
    
    Use the --dry-run option to see what would be merged without making any changes.
    Use the --limit option to process only a specific number of location groups.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--distance",
            type=float,
            default=500,
            help="Maximum distance in meters between locations to consider them as duplicates",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be merged without making any changes",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Maximum number of location groups to process",
        )

    def handle(self, *args, **options):
        distance = options["distance"]
        dry_run = options["dry_run"]
        limit = options["limit"]

        self.stdout.write(
            f"Searching for locations within {distance} meters of each other..."
        )
        nearby_pairs = find_nearby_locations(distance)

        if not nearby_pairs:
            self.stdout.write(self.style.SUCCESS("No nearby locations found to merge."))
            return

        if limit is not None:
            nearby_pairs = nearby_pairs[:limit]
            self.stdout.write(
                f"Processing {len(nearby_pairs)} groups of locations (limited by --limit option)."
            )
        else:
            self.stdout.write(
                f"Found {len(nearby_pairs)} groups of nearby locations to merge."
            )

        self.stdout.write("Location prioritization criteria:")
        self.stdout.write("1. Verified locations are preferred over non-verified")
        self.stdout.write("2. Locations with images are preferred over those without")
        self.stdout.write(
            "3. Locations with more events are preferred over those with fewer"
        )

        total_locations_to_merge = sum(
            len(merge_locs) for _, merge_locs in nearby_pairs
        )
        self.stdout.write(
            f"Total locations that will be merged: {total_locations_to_merge}"
        )
        self.stdout.write(f"Total locations that will remain: {len(nearby_pairs)}")
        self.stdout.write("=" * 50)

        for keep_loc, merge_locs in nearby_pairs:
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(
                "Location to keep (selected based on having image, most events, and being verified):"
            )
            self.stdout.write(print_location_info(keep_loc))

            self.stdout.write("\nLocations to merge:")
            for loc, dist in merge_locs:
                self.stdout.write(print_location_info(loc, dist))

            if not dry_run:
                if click.confirm(
                    "\nDo you want to merge these locations?", default=True
                ):
                    # Update all events to point to the kept location
                    total_events_updated = 0
                    for loc, _ in merge_locs:
                        event_count = loc.events.count()
                        Event.objects.filter(location=loc).update(location=keep_loc)
                        total_events_updated += event_count
                        # Delete the merged location
                        loc.delete()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Locations merged successfully. {total_events_updated} events updated to the kept location."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("Skipping this group of locations.")
                    )
            else:
                self.stdout.write(self.style.WARNING("Dry run - no changes made."))
