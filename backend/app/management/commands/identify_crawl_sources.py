"""
Management command to identify and create CrawlSources from existing events.

Groups events by (hostname, organizer) and creates CrawlSource records
for groups with a minimum number of events.
"""

from collections import defaultdict
from datetime import date
from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from tqdm import tqdm

from app.models import Event, CrawlSource, Organizer


# Known registration platforms that should not be treated as series homepages
EXCLUDED_HOSTNAMES = {
    "findarace.com",
    "reg.place",
    "gomotionapp.com",
    "active.com",
    "www.active.com",
    "raceroster.com",
    "www.raceroster.com",
    "eventbrite.com",
    "www.eventbrite.com",
    "eventbrite.co.uk",
    "webscorer.com",
    "raceentry.com",
    "reg.sportmaster.ru",
}


class Command(BaseCommand):
    help = "Identify and create CrawlSources from existing events by grouping by hostname and organizer"

    def add_arguments(self, parser):
        parser.add_argument(
            "year",
            type=int,
            nargs="?",
            default=2025,
            help="Year to analyze events for (default: 2025)",
        )
        parser.add_argument(
            "--min-events",
            type=int,
            default=3,
            help="Minimum number of events required to create a CrawlSource (default: 3)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without making changes",
        )
        parser.add_argument(
            "--organizer",
            type=int,
            help="Only process events for a specific organizer ID",
        )
        parser.add_argument(
            "--hostname",
            type=str,
            help="Only process events matching a specific hostname",
        )
        parser.add_argument(
            "--include-existing",
            action="store_true",
            help="Include events that already have a crawl_source assigned",
        )

    def handle(self, *args, **options):
        target_year = options["year"]
        min_events = options["min_events"]
        dry_run = options["dry_run"]
        organizer_id = options.get("organizer")
        hostname_filter = options.get("hostname")
        include_existing = options.get("include_existing", False)

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Running in DRY RUN mode - no changes will be made")
            )

        self.stdout.write(f"Analyzing visible events for year {target_year}")

        # Query visible events for the target year with organizers and websites
        events = (
            Event.objects.filter(
                organizer__isnull=False,
                website__isnull=False,
                invisible=False,  # Only visible events
                date_start__gte=date(target_year, 1, 1),
                date_start__lt=date(target_year + 1, 1, 1),
            )
            .exclude(website="")
            .select_related("organizer", "location")
        )

        # Filter by organizer if specified
        if organizer_id:
            events = events.filter(organizer_id=organizer_id)
            self.stdout.write(f"Filtering by organizer ID: {organizer_id}")

        # Exclude events that already have a crawl_source (unless include_existing)
        if not include_existing:
            events = events.filter(crawl_source__isnull=True)

        self.stdout.write(f"Found {events.count()} events to analyze")

        # Group events by (hostname, organizer)
        groups = defaultdict(list)
        excluded_count = 0

        for event in tqdm(events, desc="Grouping events", unit="event"):
            hostname = self._extract_hostname(event.website)
            if not hostname:
                continue

            # Filter by hostname if specified
            if hostname_filter and hostname != hostname_filter:
                continue

            # Skip excluded hostnames
            if hostname in EXCLUDED_HOSTNAMES:
                excluded_count += 1
                continue

            key = (hostname, event.organizer_id)
            groups[key].append(event)

        self.stdout.write(f"Excluded {excluded_count} events on known platforms")
        self.stdout.write(
            f"Found {len(groups)} unique (hostname, organizer) combinations"
        )

        # Filter groups with minimum events
        qualifying_groups = {k: v for k, v in groups.items() if len(v) >= min_events}

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {len(qualifying_groups)} groups with {min_events}+ events"
            )
        )

        # Create CrawlSources
        created = 0
        updated = 0
        total_events_assigned = 0

        for (hostname, organizer_id), events_list in qualifying_groups.items():
            organizer = Organizer.objects.get(id=organizer_id)

            # Build homepage URL from hostname
            homepage_url = f"https://{hostname}/"

            # Generate a name for the CrawlSource
            name = f"{organizer.name} ({hostname})"
            if len(name) > 200:
                name = f"{organizer.name[:150]}... ({hostname[:40]})"

            if dry_run:
                self.stdout.write(
                    f"Would create CrawlSource: {name}"
                    f"\n  Homepage: {homepage_url}"
                    f"\n  Organizer: {organizer.name}"
                    f"\n  Events: {len(events_list)}"
                )
            else:
                # Create or get existing CrawlSource
                crawl_source, is_created = CrawlSource.objects.get_or_create(
                    homepage_url=homepage_url,
                    organizer=organizer,
                    defaults={"name": name},
                )

                if is_created:
                    created += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Created CrawlSource: {crawl_source.name}")
                    )
                else:
                    updated += 1
                    self.stdout.write(
                        f"Using existing CrawlSource: {crawl_source.name}"
                    )

                # Assign events to CrawlSource
                for event in events_list:
                    if event.crawl_source_id != crawl_source.id:
                        event.crawl_source = crawl_source
                        event.save(update_fields=["crawl_source"])
                        total_events_assigned += 1

        # Summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\n[DRY RUN] Would create {len(qualifying_groups)} CrawlSources "
                    f"covering {sum(len(v) for v in qualifying_groups.values())} events"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nFinished:"
                    f"\n  Created: {created} CrawlSources"
                    f"\n  Existing: {updated} CrawlSources"
                    f"\n  Events assigned: {total_events_assigned}"
                )
            )

    def _extract_hostname(self, url: str) -> str:
        """Extract hostname from URL, removing www. prefix"""
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.lower()
            # Remove www. prefix for consistent matching
            if hostname.startswith("www."):
                return hostname[4:]
            return hostname
        except Exception:
            return ""
