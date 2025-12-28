from datetime import date

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Event
from app.services.google_analytics_service import GoogleAnalyticsService


class Command(BaseCommand):
    help = "Fetch Google Analytics active user counts for events"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=date.today().year,
            help="Year to fetch analytics for (default: current year)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without saving",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of events to update (for testing)",
        )

    def handle(self, *args, **options):
        year = options.get("year")
        dry_run = options.get("dry_run", False)
        limit = options.get("limit")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Running in DRY RUN mode - no changes will be saved"
                )
            )

        # Initialize service
        service = GoogleAnalyticsService(
            stdout=self.stdout,
            stderr=self.stderr,
        )

        # Fetch all event page analytics in one batch
        self.stdout.write(f"Fetching analytics data for {year}...")
        page_stats = service.fetch_page_active_users(
            year=year,
            page_path_filter="/event/",
        )

        if not page_stats:
            self.stderr.write(
                self.style.ERROR("No analytics data fetched. Check configuration.")
            )
            return

        self.stdout.write(f"Fetched {len(page_stats)} page paths from GA4")

        # Get events to update (events in the specified year with slugs)
        events_qs = Event.objects.filter(
            slug__isnull=False,
            date_start__gte=date(year, 1, 1),
            date_start__lt=date(year + 1, 1, 1),
        )

        events = list(events_qs)
        self.stdout.write(f"Found {len(events)} events in {year} with slugs")

        if not events:
            self.stdout.write(self.style.WARNING("No events found to update"))
            return

        # Match events to analytics
        self.stdout.write("Matching events to analytics data...")
        event_stats = service.match_events_to_analytics(page_stats, events)

        if not event_stats:
            self.stdout.write(
                self.style.WARNING("No events matched to analytics data")
            )
            return

        # Apply limit if specified
        if limit:
            event_ids_to_update = list(event_stats.keys())[:limit]
            event_stats = {
                k: v for k, v in event_stats.items() if k in event_ids_to_update
            }
            self.stdout.write(f"Limited to {len(event_stats)} events")

        # Update events
        updated_count = 0
        now = timezone.now()

        self.stdout.write("\nUpdating events:")
        for event_id, active_users in event_stats.items():
            try:
                event = Event.objects.get(id=event_id)

                if dry_run:
                    self.stdout.write(
                        f"  [DRY RUN] Would update {event.name} ({event.slug}): "
                        f"{active_users} active users"
                    )
                else:
                    event.active_user_count = active_users
                    event.active_user_count_updated_at = now
                    event.save(
                        update_fields=[
                            "active_user_count",
                            "active_user_count_updated_at",
                        ]
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Updated {event.name}: {active_users} active users"
                        )
                    )
                updated_count += 1

            except Event.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"  Event {event_id} not found"))

        # Summary
        prefix = "[DRY RUN] " if dry_run else ""
        total_events = len(events)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{prefix}Summary:\n"
                f"- Events with analytics: {updated_count}\n"
                f"- Events without analytics: {total_events - len(event_stats)}\n"
                f"- Total events in {year}: {total_events}"
            )
        )
