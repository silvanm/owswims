"""
Management command to batch-update events by crawling CrawlSource homepages.

Supports two source types:
- series: Events belong to same organizer, matched to existing DB events by date order
- calendar: Third-party calendar, processes each event independently (like --crawl mode)
"""

import os
import logging
from datetime import date
from django.utils import timezone
from typing import List, Optional, Dict, Tuple
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.text import slugify
import dotenv
from tqdm import tqdm

from app.models import Event, Race, CrawlSource
from app.services.event_crawler import EventCrawler
from app.services.event_processor import EventProcessor
from app.utils.url_utils import URLUtils


class Command(BaseCommand):
    help = "Update events by batch-crawling their CrawlSource homepages"

    def __init__(self):
        super().__init__()
        self.logger = None

    def add_arguments(self, parser):
        parser.add_argument(
            "year",
            type=int,
            help="Target year to update events for (e.g., 2026)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of CrawlSources to process (for debugging)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform processing without saving changes to the database",
        )
        parser.add_argument(
            "--crawl-source",
            type=int,
            help="Only process a specific CrawlSource by ID",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update all CrawlSources, ignoring last_crawled_at",
        )
        parser.add_argument(
            "--check-interval",
            type=int,
            default=0,
            help="Skip CrawlSources crawled within this many days (default: 0, meaning skip if crawled this year)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process ALL CrawlSources, not just those with events in target year",
        )

    def handle(self, *args, **options):
        dotenv.load_dotenv()
        api_key = os.environ["FIRECRAWL_API_KEY"]
        target_year = options["year"]
        limit = options.get("limit")
        dry_run = options.get("dry_run", False)
        crawl_source_id = options.get("crawl_source")
        force = options.get("force", False)
        check_interval_days = options.get("check_interval", 30)
        process_all = options.get("all", False)

        # Set up logging
        self._setup_logging()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Running in DRY RUN mode - no database changes will be made"
                )
            )

        # Get CrawlSources to process
        crawl_sources = self._get_crawl_sources_to_update(
            target_year, crawl_source_id, force, check_interval_days, limit, process_all
        )

        if not crawl_sources:
            self.stdout.write(
                self.style.WARNING(f"No CrawlSources found to update for {target_year}")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(crawl_sources)} CrawlSources to process")
        )

        # Create processor and crawler
        processor = EventProcessor(
            firecrawl_api_key=api_key,
            stdout=self.stdout,
            stderr=self.stderr,
            dry_run=dry_run,
        )

        crawler = EventCrawler(
            firecrawl_api_key=api_key,
            stdout=self.stdout,
            stderr=self.stderr,
        )

        # Process each CrawlSource
        successful_sources = 0
        failed_sources = 0
        events_updated = 0
        events_not_found = 0
        events_created = 0
        events_skipped = 0

        progress_bar = tqdm(
            crawl_sources,
            desc="Processing CrawlSources",
            unit="source",
            ncols=100,
        )

        for crawl_source in progress_bar:
            progress_bar.set_postfix_str(f"{crawl_source.name[:30]}...")
            self.logger.info(
                f"Processing CrawlSource: {crawl_source.name} (ID: {crawl_source.id}, type: {crawl_source.source_type})"
            )

            try:
                # Dispatch based on source type
                if crawl_source.source_type == "calendar":
                    result = self._update_calendar_source(
                        crawl_source, processor, crawler, target_year, dry_run
                    )
                else:
                    result = self._update_series_source(
                        crawl_source, processor, crawler, target_year, dry_run
                    )

                if result["success"]:
                    successful_sources += 1
                    events_updated += result.get("updated", 0)
                    events_not_found += result.get("not_found", 0)
                    events_created += result.get("created", 0)  # Both series and calendar
                    events_skipped += result.get("skipped", 0)
                else:
                    failed_sources += 1

            except Exception as e:
                tqdm.write(
                    self.style.ERROR(f"Failed to process CrawlSource: {str(e)}")
                )
                self.logger.error(
                    f"Failed to process CrawlSource {crawl_source.id}: {str(e)}"
                )
                failed_sources += 1

            # Update progress bar
            progress_bar.set_description(
                f"OK:{successful_sources} FAIL:{failed_sources}"
            )

        # Summary
        dry_run_prefix = "[DRY RUN] " if dry_run else ""
        summary_lines = [
            f"\n{dry_run_prefix}Finished updating CrawlSources:",
            f"- Successful CrawlSources: {successful_sources}",
            f"- Failed CrawlSources: {failed_sources}",
            f"- Events updated: {events_updated}",
            f"- Events created: {events_created}",
            f"- Events skipped (already exist): {events_skipped}",
            f"- Events not matched: {events_not_found}",
            f"- Total CrawlSources processed: {len(crawl_sources)}",
        ]

        self.stdout.write(self.style.SUCCESS("\n".join(summary_lines)))

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "No database changes were made. Run without --dry-run to save updates."
                )
            )

    def _setup_logging(self):
        """Set up file logging"""
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "..",
            "logs",
        )
        os.makedirs(log_dir, exist_ok=True)

        log_filename = os.path.join(
            log_dir, f"update_crawl_sources_{timezone.now().strftime('%Y%m%d')}.log"
        )

        self.logger = logging.getLogger("update_crawl_sources")
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers
        self.logger.handlers = []

        # File handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _get_crawl_sources_to_update(
        self,
        target_year: int,
        crawl_source_id: Optional[int] = None,
        force: bool = False,
        check_interval_days: int = 30,
        limit: Optional[int] = None,
        process_all: bool = False,
    ) -> List[CrawlSource]:
        """Get CrawlSources to update.

        If process_all is True: returns ALL CrawlSources
        Otherwise:
        - For 'series' type: must have events for the target year
        - For 'calendar' type: always included (discovers new events)
        """
        from datetime import timedelta

        if process_all:
            # Return all CrawlSources
            crawl_sources = CrawlSource.objects.all()
        else:
            # Get series CrawlSources with events in the target year
            series_sources = CrawlSource.objects.filter(
                source_type="series",
                events__date_start__gte=date(target_year, 1, 1),
                events__date_start__lt=date(target_year + 1, 1, 1),
                events__invisible=True,  # Only unverified/invisible events
                events__verified_at__isnull=True,
            ).distinct()

            # Get all calendar CrawlSources (they discover new events)
            calendar_sources = CrawlSource.objects.filter(source_type="calendar")

            # Combine both querysets
            crawl_sources = series_sources.union(calendar_sources)

        # Filter by specific ID if provided
        if crawl_source_id:
            crawl_sources = CrawlSource.objects.filter(id=crawl_source_id)

        # Apply check interval filter unless force is True
        if not force:
            if check_interval_days > 0:
                # Skip if crawled within N days
                cutoff_date = timezone.now() - timedelta(days=check_interval_days)
            else:
                # Default: skip if already crawled this year
                cutoff_date = timezone.make_aware(
                    timezone.datetime(timezone.now().year, 1, 1)
                )

            # Need to filter on original queryset since union doesn't support filter
            if crawl_source_id or process_all:
                crawl_sources = crawl_sources.filter(
                    Q(last_crawled_at__isnull=True) | Q(last_crawled_at__lt=cutoff_date)
                )
            else:
                # Re-query with filter applied
                series_sources = series_sources.filter(
                    Q(last_crawled_at__isnull=True) | Q(last_crawled_at__lt=cutoff_date)
                )
                calendar_sources = calendar_sources.filter(
                    Q(last_crawled_at__isnull=True) | Q(last_crawled_at__lt=cutoff_date)
                )
                crawl_sources = series_sources.union(calendar_sources)

        # Apply limit
        result = list(crawl_sources)
        if limit and limit > 0:
            result = result[:limit]

        return result

    def _update_series_source(
        self,
        crawl_source: CrawlSource,
        processor: EventProcessor,
        crawler: EventCrawler,
        target_year: int,
        dry_run: bool,
    ) -> Dict:
        """
        Update events for a 'series' type CrawlSource.

        Crawls the homepage and:
        - If DB events exist for target year: matches and updates them by date order
        - If no DB events exist: creates new events for the target year

        Returns:
            Dict with 'success', 'updated', 'not_found', 'created' counts
        """
        result = {"success": False, "updated": 0, "not_found": 0, "created": 0}

        # Get DB events for this CrawlSource and target year
        db_events = list(
            Event.objects.filter(
                crawl_source=crawl_source,
                date_start__gte=date(target_year, 1, 1),
                date_start__lt=date(target_year + 1, 1, 1),
            ).order_by("date_start")
        )

        if db_events:
            self.stdout.write(
                f"Found {len(db_events)} existing DB events for {crawl_source.name}"
            )
        else:
            self.stdout.write(
                f"No existing events for {crawl_source.name} in {target_year} - will create new ones"
            )

        # Crawl the homepage
        self.stdout.write(f"Crawling {crawl_source.homepage_url}")
        self.logger.info(f"Crawling homepage: {crawl_source.homepage_url}")

        try:
            event_url_sets = crawler.get_event_urls(crawl_source.homepage_url)
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to crawl homepage: {str(e)}")
            )
            self.logger.error(f"Failed to crawl homepage: {str(e)}")
            return result

        if not event_url_sets:
            self.stdout.write(
                self.style.WARNING(f"No events found on {crawl_source.homepage_url}")
            )
            return result

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {len(event_url_sets)} events on homepage"
            )
        )

        # Extract data from each URL set
        extracted_events = []
        for urls in event_url_sets:
            try:
                event_data = processor.extract_event_data(
                    urls=urls,
                    target_year=target_year,
                    filter_future_only=False,
                )
                if event_data and event_data.get("event"):
                    event_data["_urls"] = urls  # Store source URLs
                    extracted_events.append(event_data)
            except Exception as e:
                self.logger.error(f"Failed to extract data from {urls}: {str(e)}")
                continue

        if not extracted_events:
            self.stdout.write(
                self.style.WARNING("No valid events extracted from homepage")
            )
            return result

        self.stdout.write(f"Extracted {len(extracted_events)} valid events")

        # Sort extracted events by date (handle None values)
        extracted_events.sort(
            key=lambda x: x["event"].get("date_start") or "9999-99-99"
        )

        # Filter to only events in target year (handle None values)
        target_year_events = [
            e for e in extracted_events
            if (e["event"].get("date_start") or "").startswith(str(target_year))
        ]

        if not target_year_events:
            self.stdout.write(
                self.style.WARNING(f"No events for {target_year} found on homepage")
            )
            result["success"] = True
            if not dry_run:
                crawl_source.last_crawled_at = timezone.now()
                crawl_source.save(update_fields=["last_crawled_at"])
            return result

        self.stdout.write(f"Found {len(target_year_events)} events for {target_year}")

        if db_events:
            # Match by date order to existing events
            matches = self._match_events_by_date_order(target_year_events, db_events)

            # Log matching results
            self.stdout.write(f"Matched {len(matches)} events by date order")
            if len(target_year_events) != len(db_events):
                self.stdout.write(
                    self.style.WARNING(
                        f"Count mismatch: {len(target_year_events)} extracted vs {len(db_events)} in DB"
                    )
                )
                self.logger.warning(
                    f"Count mismatch for CrawlSource {crawl_source.id}: "
                    f"{len(target_year_events)} extracted vs {len(db_events)} in DB"
                )

            # Apply updates to matched events
            for extracted, db_event in matches:
                try:
                    urls = extracted.get("_urls", [])
                    success = self._apply_updates(db_event, extracted, urls, dry_run)
                    if success:
                        result["updated"] += 1
                    else:
                        result["not_found"] += 1
                except Exception as e:
                    self.logger.error(
                        f"Failed to update event {db_event.id}: {str(e)}"
                    )
                    result["not_found"] += 1
        else:
            # No existing events - create new ones
            # First, filter out URLs that already exist in the database
            url_sets_to_create = [e.get("_urls", []) for e in target_year_events]
            filtered_url_sets = URLUtils.filter_existing_url_sets(
                url_sets_to_create, stdout=self.stdout, stderr=self.stderr
            )

            # Build a set of URLs that passed the filter
            filtered_urls = set()
            for url_set in filtered_url_sets:
                for url in url_set:
                    filtered_urls.add(url)

            for extracted in target_year_events:
                try:
                    urls = extracted.get("_urls", [])

                    # Skip if URL already exists in database
                    if urls and not any(url in filtered_urls for url in urls):
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping (already exists): {extracted['event'].get('name')}"
                            )
                        )
                        result["skipped"] = result.get("skipped", 0) + 1
                        continue

                    if dry_run:
                        self.stdout.write(
                            self.style.WARNING(
                                f"[DRY RUN] Would create event: {extracted['event'].get('name')}"
                            )
                        )
                        result["created"] += 1
                    else:
                        event = self._create_event(extracted, urls, crawl_source)
                        if event:
                            result["created"] += 1
                            self.logger.info(f"Created event {event.id}: {event.name}")
                        else:
                            result["not_found"] += 1
                except Exception as e:
                    self.logger.error(f"Failed to create event: {str(e)}")
                    result["not_found"] += 1

        # Update last_crawled_at on CrawlSource
        if not dry_run:
            crawl_source.last_crawled_at = timezone.now()
            crawl_source.save(update_fields=["last_crawled_at"])

        result["success"] = True
        return result

    def _match_events_by_date_order(
        self,
        extracted_events: List[Dict],
        db_events: List[Event],
    ) -> List[Tuple[Dict, Event]]:
        """
        Match extracted events to DB events by date order.

        Both lists should already be sorted by date.
        Returns a list of (extracted_data, db_event) tuples.
        """
        matches = []
        min_len = min(len(extracted_events), len(db_events))

        for i in range(min_len):
            matches.append((extracted_events[i], db_events[i]))

        return matches

    def _apply_updates(
        self, event: Event, event_data: Dict, urls: List[str], dry_run: bool
    ) -> bool:
        """
        Apply updates to the event from extracted data.

        Returns: True if successful, False otherwise
        """
        try:
            from djmoney.money import Money

            new_event_data = event_data["event"]
            races_data = event_data.get("races", [])

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f"[DRY RUN] Would update event: {event.name}")
                )
                self.stdout.write(f"  New name: {new_event_data.get('name')}")
                self.stdout.write(
                    f"  Dates: {new_event_data.get('date_start')} to {new_event_data.get('date_end')}"
                )
                self.stdout.write(f"  Races: {len(races_data)}")
                return True

            # Update event fields (preserve location and organizer)
            event.name = new_event_data.get("name", event.name)
            event.website = new_event_data.get("website", urls[0] if urls else event.website)
            event.slug = slugify(event.name)
            event.date_start = new_event_data.get("date_start", event.date_start)
            event.date_end = new_event_data.get("date_end", event.date_end)
            event.description = new_event_data.get("description", event.description) or ""
            event.water_temp = new_event_data.get("water_temp")
            event.needs_medical_certificate = new_event_data.get(
                "needs_medical_certificate", event.needs_medical_certificate
            )
            event.needs_license = new_event_data.get("needs_license", event.needs_license)
            event.sold_out = new_event_data.get("sold_out", event.sold_out)
            event.cancelled = new_event_data.get("cancelled", event.cancelled)
            event.with_ranking = new_event_data.get("with_ranking", event.with_ranking)

            # Update source (truncate to fit max_length=200)
            source_text = f"Auto-updated via CrawlSource: {', '.join(urls)}"
            event.source = source_text[:200] if len(source_text) > 200 else source_text

            # Make visible but keep unverified
            event.invisible = False
            event.last_auto_check_at = timezone.now()

            event.save()

            # Delete old races and create new ones
            event.races.all().delete()

            for race_data in races_data:
                price_amount = race_data.get("price", {}).get("amount")
                price_currency = race_data.get("price", {}).get("currency", "EUR")

                race_kwargs = {
                    "event": event,
                    "name": race_data["name"],
                    "date": race_data["date"],
                    "race_time": race_data.get("race_time"),
                    "distance": race_data.get("distance"),
                    "wetsuit": race_data.get("wetsuit"),
                }

                if price_amount is not None:
                    race_kwargs["price"] = Money(price_amount, price_currency)

                Race.objects.create(**race_kwargs)

            self.logger.info(f"Successfully updated event {event.id}: {event.name}")
            return True

        except Exception as e:
            self.logger.error(f"Error applying updates to event {event.id}: {str(e)}")
            return False

    def _create_event(
        self, event_data: Dict, urls: List[str], crawl_source: CrawlSource
    ) -> Optional[Event]:
        """
        Create a new event from extracted data.

        Returns: Created Event or None on failure
        """
        from djmoney.money import Money
        from app.services.geocoding_service import GeocodingService

        try:
            new_event_data = event_data["event"]
            races_data = event_data.get("races", [])
            location_data = event_data.get("location", {})

            # Get or create location
            location = None
            if location_data:
                geocoding_service = GeocodingService()
                location = geocoding_service.get_or_create_location(
                    address=location_data.get("address", ""),
                    body_of_water=location_data.get("body_of_water", ""),
                )

            # Create the event
            event = Event.objects.create(
                name=new_event_data.get("name", "Unknown Event"),
                slug=slugify(new_event_data.get("name", "unknown-event")),
                website=new_event_data.get("website", urls[0] if urls else ""),
                date_start=new_event_data.get("date_start"),
                date_end=new_event_data.get("date_end"),
                description=new_event_data.get("description", "") or "",
                water_temp=new_event_data.get("water_temp"),
                needs_medical_certificate=new_event_data.get("needs_medical_certificate", False),
                needs_license=new_event_data.get("needs_license", False),
                sold_out=new_event_data.get("sold_out", False),
                cancelled=new_event_data.get("cancelled", False),
                with_ranking=new_event_data.get("with_ranking", False),
                location=location,
                organizer=crawl_source.organizer,
                crawl_source=crawl_source,
                source=f"Auto-created via CrawlSource: {urls[0] if urls else crawl_source.homepage_url}"[:200],
                invisible=False,
                last_auto_check_at=timezone.now(),
            )

            # Create races
            for race_data in races_data:
                price_amount = race_data.get("price", {}).get("amount")
                price_currency = race_data.get("price", {}).get("currency", "EUR")

                race_kwargs = {
                    "event": event,
                    "name": race_data["name"],
                    "date": race_data["date"],
                    "race_time": race_data.get("race_time"),
                    "distance": race_data.get("distance"),
                    "wetsuit": race_data.get("wetsuit"),
                }

                if price_amount is not None:
                    race_kwargs["price"] = Money(price_amount, price_currency)

                Race.objects.create(**race_kwargs)

            self.stdout.write(
                self.style.SUCCESS(f"Created event: {event.name} ({event.date_start})")
            )
            return event

        except Exception as e:
            self.logger.error(f"Error creating event: {str(e)}")
            return None

    def _update_calendar_source(
        self,
        crawl_source: CrawlSource,
        processor: EventProcessor,
        crawler: EventCrawler,
        target_year: int,
        dry_run: bool,
    ) -> Dict:
        """
        Process a 'calendar' type CrawlSource.

        Works like --crawl mode: crawls the homepage, filters out existing URLs,
        and processes each new event independently.

        Returns:
            Dict with 'success', 'created', 'skipped' counts
        """
        result = {"success": False, "created": 0, "skipped": 0}

        # Crawl the homepage
        self.stdout.write(f"Crawling calendar: {crawl_source.homepage_url}")
        self.logger.info(f"Crawling calendar homepage: {crawl_source.homepage_url}")

        try:
            event_url_sets = crawler.get_event_urls(crawl_source.homepage_url)
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Failed to crawl calendar homepage: {str(e)}")
            )
            self.logger.error(f"Failed to crawl calendar homepage: {str(e)}")
            return result

        if not event_url_sets:
            self.stdout.write(
                self.style.WARNING(f"No events found on {crawl_source.homepage_url}")
            )
            # Still mark as success since crawl completed
            result["success"] = True
            if not dry_run:
                crawl_source.last_crawled_at = timezone.now()
                crawl_source.save(update_fields=["last_crawled_at"])
            return result

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(event_url_sets)} events on calendar")
        )

        # Filter out URLs that already exist in the database
        self.stdout.write("Filtering out URLs that already exist in the database...")
        filtered_url_sets = URLUtils.filter_existing_url_sets(
            event_url_sets, stdout=self.stdout, stderr=self.stderr
        )

        skipped_count = len(event_url_sets) - len(filtered_url_sets)
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f"Skipping {skipped_count} events that already exist")
            )
            result["skipped"] = skipped_count

        if not filtered_url_sets:
            self.stdout.write(
                self.style.WARNING("All events already exist in the database")
            )
            result["success"] = True
            if not dry_run:
                crawl_source.last_crawled_at = timezone.now()
                crawl_source.save(update_fields=["last_crawled_at"])
            return result

        self.stdout.write(f"Processing {len(filtered_url_sets)} new events")

        # Process each event URL set
        for urls in filtered_url_sets:
            try:
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f"[DRY RUN] Would process event: {urls[0]}")
                    )
                    result["created"] += 1
                else:
                    event = processor.process_event_urls(urls)
                    if event:
                        # Link the event to this CrawlSource
                        event.crawl_source = crawl_source
                        event.save(update_fields=["crawl_source"])
                        self.logger.info(
                            f"Created event {event.id}: {event.name} from {urls[0]}"
                        )
                        result["created"] += 1
                    else:
                        self.logger.warning(f"Failed to process event from {urls[0]}")
            except Exception as e:
                self.logger.error(f"Failed to process event from {urls}: {str(e)}")
                continue

        # Update last_crawled_at on CrawlSource
        if not dry_run:
            crawl_source.last_crawled_at = timezone.now()
            crawl_source.save(update_fields=["last_crawled_at"])

        result["success"] = True
        return result
