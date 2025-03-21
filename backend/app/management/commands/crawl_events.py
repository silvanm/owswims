import os
from typing import List
from django.core.management.base import BaseCommand
import dotenv

from app.services.event_processor import EventProcessor
from app.services.event_crawler import EventCrawler


class Command(BaseCommand):
    help = "Crawl and process swimming events. Can process a single event or crawl multiple events from a website."

    def add_arguments(self, parser):
        # Create a mutually exclusive group for the mode
        mode_group = parser.add_mutually_exclusive_group(required=True)
        mode_group.add_argument(
            "--event",
            nargs="+",
            type=str,
            help="Process a single event. Provide one or more URLs for the same event.",
        )
        mode_group.add_argument(
            "--crawl",
            type=str,
            help="Crawl multiple events from a website (e.g., https://oceanmanswim.com/events/)",
        )
        mode_group.add_argument(
            "--profile",
            type=str,
            help="Use a specific crawl profile (e.g., outdoorswimmer)",
        )

        # Optional arguments
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of events to process (for debugging)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform crawling and processing without saving to the database",
        )

    def handle(self, *args, **options):
        dotenv.load_dotenv()
        api_key = os.environ["FIRECRAWL_API_KEY"]
        dry_run = options.get("dry_run", False)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Running in DRY RUN mode - no database changes will be made"
                )
            )

        processor = EventProcessor(
            firecrawl_api_key=api_key,
            stdout=self.stdout,
            stderr=self.stderr,
            dry_run=dry_run,
        )

        if options["event"]:
            # Process single event mode
            result = self._process_single_event(processor, options["event"])
            # Add a reminder about dry run mode if applicable
            if dry_run and result:
                self.stdout.write(
                    self.style.WARNING(
                        "No database changes were made. Run without --dry-run to save events to the database."
                    )
                )
        elif options["profile"]:
            # Profile-based crawling mode
            self._crawl_with_profile(
                processor, api_key, options["profile"], limit=options.get("limit")
            )
        else:
            # Crawl multiple events mode
            self._crawl_multiple_events(
                processor, api_key, options["crawl"], limit=options.get("limit")
            )

    def _process_single_event(self, processor: EventProcessor, urls: List[str]):
        """Process a single event from provided URLs"""
        self.stdout.write(f"Processing event URLs: {', '.join(urls)}")
        event = processor.process_event_urls(urls)

        if event:
            if processor.dry_run:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[DRY RUN] Successfully processed event: {event.name} (would be saved to database)"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully processed event: {event.name} (ID: {event.id})"
                    )
                )
            return True
        else:
            dry_run_prefix = "[DRY RUN] " if processor.dry_run else ""
            self.stdout.write(
                self.style.ERROR(f"{dry_run_prefix}Failed to process event.")
            )
            return False

    def _crawl_multiple_events(
        self, processor: EventProcessor, api_key: str, start_url: str, limit: int = None
    ):
        """Crawl and process multiple events from a website"""
        crawler = EventCrawler(
            firecrawl_api_key=api_key,
            stdout=self.stdout,
            stderr=self.stderr,
        )

        # Get event URLs
        self.stdout.write(f"Crawling events from {start_url}")
        event_url_sets = crawler.get_event_urls(start_url)

        if not event_url_sets:
            self.stdout.write(self.style.WARNING("No events found"))
            return

        # Apply limit if specified
        if limit and limit > 0:
            original_count = len(event_url_sets)
            event_url_sets = event_url_sets[:limit]
            self.stdout.write(
                self.style.WARNING(
                    f"Limiting to {limit} events (found {original_count} total)"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"Processing {len(event_url_sets)} events")
        )

        # Process each event
        successful = 0
        failed = 0
        for i, urls in enumerate(event_url_sets, 1):
            self.stdout.write(f"Processing event {i}/{len(event_url_sets)}")
            try:
                if self._process_single_event(processor, urls):
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Failed to process event: {str(e)}")
                )
                failed += 1

        # Summary
        dry_run_prefix = "[DRY RUN] " if processor.dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{dry_run_prefix}Finished processing events:\n"
                f"- Successful: {successful}\n"
                f"- Failed: {failed}\n"
                f"- Total: {len(event_url_sets)}"
            )
        )

        if processor.dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "No database changes were made. Run without --dry-run to save events to the database."
                )
            )

    def _crawl_with_profile(
        self,
        processor: EventProcessor,
        api_key: str,
        profile_id: str,
        limit: int = None,
    ):
        """Crawl and process events using a specific profile"""
        from app.crawl_profiles.profiles import get_profile

        # Load the profile
        profile = get_profile(profile_id)
        if not profile:
            self.stderr.write(self.style.ERROR(f"Profile '{profile_id}' not found"))
            return

        # Get the start URL from the profile
        start_url = profile.get("start_url")
        if not start_url:
            self.stderr.write(
                self.style.ERROR(f"Profile '{profile_id}' does not contain a start_url")
            )
            return

        # Create a crawler with the profile
        crawler = EventCrawler(
            firecrawl_api_key=api_key,
            stdout=self.stdout,
            stderr=self.stderr,
            profile=profile,  # Pass the profile to the crawler
        )

        # Get event URLs
        self.stdout.write(
            f"Crawling events from {start_url} using profile '{profile.get('name', profile_id)}'"
        )
        event_url_sets = crawler.get_event_urls(start_url)

        if not event_url_sets:
            self.stdout.write(self.style.WARNING("No events found"))
            return

        # Apply limit if specified
        if limit and limit > 0:
            original_count = len(event_url_sets)
            event_url_sets = event_url_sets[:limit]
            self.stdout.write(
                self.style.WARNING(
                    f"Limiting to {limit} events (found {original_count} total)"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"Processing {len(event_url_sets)} events")
        )

        # Process each event
        successful = 0
        failed = 0
        for i, urls in enumerate(event_url_sets, 1):
            self.stdout.write(f"Processing event {i}/{len(event_url_sets)}")
            try:
                if self._process_single_event(processor, urls):
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Failed to process event: {str(e)}")
                )
                failed += 1

        # Summary
        dry_run_prefix = "[DRY RUN] " if processor.dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{dry_run_prefix}Finished processing events:\n"
                f"- Successful: {successful}\n"
                f"- Failed: {failed}\n"
                f"- Total: {len(event_url_sets)}"
            )
        )

        if processor.dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "No database changes were made. Run without --dry-run to save events to the database."
                )
            )
