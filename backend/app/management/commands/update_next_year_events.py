import os
import logging
from datetime import datetime, date
from typing import List, Optional, Dict
from django.core.management.base import BaseCommand
from django.utils.text import slugify
import dotenv

from app.models import Event, Race
from app.services.event_crawler import EventCrawler
from app.services.event_processor import EventProcessor


class Command(BaseCommand):
    help = "Update next year's events by searching for updated information on their websites"

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
            help="Limit the number of events to process (for debugging)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform processing without saving changes to the database",
        )
        parser.add_argument(
            "--check-interval",
            type=int,
            default=30,
            help="Skip events checked within this many days (default: 30). Set to 0 to check all events.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force check all events, ignoring last check date",
        )

    def handle(self, *args, **options):
        dotenv.load_dotenv()
        api_key = os.environ["FIRECRAWL_API_KEY"]
        target_year = options["year"]
        limit = options.get("limit")
        dry_run = options.get("dry_run", False)
        check_interval_days = options.get("check_interval", 30)
        force = options.get("force", False)

        # Set up logging
        self._setup_logging()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Running in DRY RUN mode - no database changes will be made"
                )
            )

        if force:
            self.stdout.write(
                self.style.WARNING(
                    "Force mode enabled - checking all events regardless of last check date"
                )
            )
        elif check_interval_days > 0:
            self.stdout.write(
                f"Checking events not checked in the last {check_interval_days} days"
            )

        # Query events for the target year
        self.stdout.write(f"Searching for events to update for year {target_year}")
        events = self._get_events_to_update(target_year, limit, check_interval_days, force)

        if not events:
            self.stdout.write(
                self.style.WARNING(f"No events found to update for {target_year}")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(events)} events to process")
        )

        # Create processor
        processor = EventProcessor(
            firecrawl_api_key=api_key,
            stdout=self.stdout,
            stderr=self.stderr,
            dry_run=dry_run,
        )

        # Create crawler for searching
        crawler = EventCrawler(
            firecrawl_api_key=api_key,
            stdout=self.stdout,
            stderr=self.stderr,
        )

        # Process each event
        successful = 0
        failed = 0
        not_found = 0

        for i, event in enumerate(events, 1):
            self.stdout.write(
                f"\nProcessing event {i}/{len(events)}: {event.name} (ID: {event.id})"
            )
            self.logger.info(f"Processing event: {event.name} (ID: {event.id})")

            try:
                result = self._update_event(
                    event, processor, crawler, target_year, dry_run
                )
                if result == "success":
                    successful += 1
                elif result == "not_found":
                    not_found += 1
                else:
                    failed += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Failed to process event: {str(e)}")
                )
                self.logger.error(f"Failed to process event {event.id}: {str(e)}")
                self._append_internal_comment(
                    event, f"ERROR: Failed to process: {str(e)}", dry_run
                )
                failed += 1

        # Summary
        dry_run_prefix = "[DRY RUN] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{dry_run_prefix}Finished updating events:\n"
                f"- Successfully updated: {successful}\n"
                f"- Not found (no {target_year} info): {not_found}\n"
                f"- Failed: {failed}\n"
                f"- Total processed: {len(events)}"
            )
        )

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
            log_dir, f"update_next_year_events_{datetime.now().strftime('%Y%m%d')}.log"
        )

        self.logger = logging.getLogger("update_next_year_events")
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

    def _get_events_to_update(
        self,
        target_year: int,
        limit: Optional[int] = None,
        check_interval_days: int = 30,
        force: bool = False
    ) -> List[Event]:
        """Query events for the target year that need updating"""
        from django.db.models import Q
        from datetime import timedelta

        events = Event.objects.filter(
            date_start__gte=date(target_year, 1, 1),
            date_start__lt=date(target_year + 1, 1, 1),
            invisible=True,
            verified_at__isnull=True,
            previous_year_event__isnull=False,
        ).select_related("location", "organizer", "previous_year_event")

        # Apply check interval filter unless force is True
        if not force and check_interval_days > 0:
            from datetime import datetime
            cutoff_date = datetime.now() - timedelta(days=check_interval_days)
            events = events.filter(
                Q(last_auto_check_at__isnull=True) |  # Never checked
                Q(last_auto_check_at__lt=cutoff_date)  # Last checked before cutoff
            )

        if limit and limit > 0:
            events = events[:limit]

        return list(events)

    def _update_event(
        self,
        event: Event,
        processor: EventProcessor,
        crawler: EventCrawler,
        target_year: int,
        dry_run: bool,
    ) -> str:
        """
        Update a single event by searching for next year's information

        Returns: 'success', 'not_found', or 'failed'
        """
        if not event.website:
            self.stdout.write(
                self.style.WARNING(f"Event {event.name} has no website, skipping")
            )
            self._append_internal_comment(
                event, "Skipped: No website URL available", dry_run
            )
            return "not_found"

        # Log the search attempt
        self._append_internal_comment(
            event, f"Searching for {target_year} information at {event.website}", dry_run
        )

        # Search for next year's event URLs
        self.stdout.write(f"Searching {event.website} for {target_year} information")
        self.logger.info(
            f"Searching {event.website} for {target_year} event: {event.name}"
        )

        event_url_sets = self._search_for_next_year_event(
            event, crawler, target_year
        )

        if not event_url_sets:
            self.stdout.write(
                self.style.WARNING(
                    f"No {target_year} information found for {event.name}"
                )
            )
            self.logger.info(f"No {target_year} information found for event {event.id}")
            self._append_internal_comment(
                event, f"No {target_year} information found on website", dry_run
            )
            # Update last check timestamp
            if not dry_run:
                from datetime import datetime
                event.last_auto_check_at = datetime.now()
                event.save(update_fields=['last_auto_check_at'])
            return "not_found"

        # Process the URLs to get structured data
        urls = event_url_sets[0]  # Take the first set of URLs
        self.stdout.write(f"Found URLs: {', '.join(urls)}")
        self.logger.info(f"Found URLs for event {event.id}: {urls}")

        # Extract event data from URLs (without saving to database)
        self.stdout.write("Extracting event data from URLs")
        event_data = self._extract_event_data(processor, urls, target_year)

        if not event_data:
            self.stderr.write(
                self.style.ERROR("Failed to extract data from URLs")
            )
            self.logger.error(f"Failed to extract data from URLs for event {event.id}")
            self._append_internal_comment(
                event, "Failed to extract data from found URLs", dry_run
            )
            # Update last check timestamp
            if not dry_run:
                from datetime import datetime
                event.last_auto_check_at = datetime.now()
                event.save(update_fields=['last_auto_check_at'])
            return "failed"

        # Check if the extracted event is for the target year
        from datetime import datetime
        extracted_date = datetime.strptime(
            event_data["event"]["date_start"], "%Y-%m-%d"
        ).date()

        if extracted_date.year != target_year:
            self.stdout.write(
                self.style.WARNING(
                    f"Found event for {extracted_date.year}, but looking for {target_year}"
                )
            )
            self.logger.info(
                f"Event {event.id}: Found {extracted_date.year} edition, not {target_year}"
            )
            self._append_internal_comment(
                event,
                f"Found {extracted_date.year} edition on website, but looking for {target_year}",
                dry_run
            )
            # Update last check timestamp
            if not dry_run:
                event.last_auto_check_at = datetime.now()
                event.save(update_fields=['last_auto_check_at'])
            return "not_found"

        # Update the event with new data
        self.stdout.write("Updating event with new data")
        success = self._apply_updates(event, event_data, urls, dry_run)

        if success:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated event: {event.name}")
            )
            self.logger.info(f"Successfully updated event {event.id}")
            self._append_internal_comment(
                event, f"Successfully updated with data from: {', '.join(urls)}", dry_run
            )
            # Update last check timestamp
            if not dry_run:
                event.last_auto_check_at = datetime.now()
                event.save(update_fields=['last_auto_check_at'])
            return "success"
        else:
            self.stderr.write(
                self.style.ERROR(f"Failed to update event: {event.name}")
            )
            self.logger.error(f"Failed to update event {event.id}")
            self._append_internal_comment(
                event, "Failed to apply updates to event", dry_run
            )
            # Update last check timestamp
            if not dry_run:
                event.last_auto_check_at = datetime.now()
                event.save(update_fields=['last_auto_check_at'])
            return "failed"

    def _search_for_next_year_event(
        self, event: Event, crawler: EventCrawler, target_year: int
    ) -> List[List[str]]:
        """
        Use EventCrawler to search for next year's event information

        Returns: List of URL sets (each set represents one event)
        """
        # Try to get event URLs from the website
        # This uses the existing crawler which may find multiple events
        # We'll filter for the most relevant one
        try:
            event_url_sets = crawler.get_event_urls(event.website)
            # Filter for URLs that might be relevant (this is a simple heuristic)
            # In practice, the LLM should find the right event
            return event_url_sets[:1] if event_url_sets else []
        except Exception as e:
            self.logger.error(
                f"Error searching for event {event.id}: {str(e)}"
            )
            return []

    def _extract_event_data(
        self, processor: EventProcessor, urls: List[str], target_year: int = None
    ) -> Optional[Dict]:
        """
        Extract event data from URLs without saving to database

        Returns: Dictionary with event and races data, or None if extraction failed
        """
        try:
            import json
            import re
            from llama_index.core.tools import FunctionTool
            from llama_index.core.agent import ReActAgent
            from datetime import datetime

            # Scrape the content
            contents = []
            for url in urls:
                self.logger.info(f"Scraping URL: {url}")
                content = processor.scraping_service.scrape(url)
                if content:
                    contents.append({"url": url, "content": content})

            if not contents:
                return None

            # Create agent to extract data
            scrape_tool = FunctionTool.from_defaults(fn=processor.scraping_service.scrape)
            agent = ReActAgent.from_tools(
                [scrape_tool], max_iterations=20, llm=processor.llm, verbose=True
            )

            current_date = datetime.now().strftime("%Y-%m-%d")

            # Build year-specific instruction
            year_instruction = ""
            if target_year:
                year_instruction = f"""
IMPORTANT: You are specifically looking for the {target_year} edition of this event.
If the page shows multiple years (e.g., {target_year-1} and {target_year}), extract information for {target_year} only.
If you only find information for a different year (like {target_year-1}), extract that data anyway - we will validate the year later.
Look for links or navigation to the {target_year} edition if available.
"""

            # Use the same prompt as EventProcessor
            prompt = f"""Analyze these pages about an open water swimming event.
Visit the following URLs to gather information about a swim event: {', '.join(urls)}
These URLs contain details about the same event. Please analyze all pages and combine the information to create a complete event profile.

Today's date is {current_date}. Process all events regardless of their date.
{year_instruction}

If the page is not about a single open water swim event, skip it.

If the event has an item "Links" which appears to include more information about it, follow it.

To find out the price of the event, look for the registration page ("Anmeldung" or "Ausschreibung") or the page where you can buy tickets.

If the event is virtual or does not have a physical location, skip it.

Pay attention to the distance of the race. On US sites it is often given in miles. You need to convert it to kilometers.

Pay attention to the date of the event. On US sites it is often given in the format "15th of July 2024". You need to convert it to the format "2024-07-15".

IMPORTANT: For the country field, you MUST use ISO 3166-1 alpha-2 country codes in Latin letters only. Examples:
- Japan = "JP" (not "日本")
- Germany = "DE" (not "Deutschland")
- United Kingdom = "GB" (not "UK")
- United States = "US" (not "USA")
- Switzerland = "CH" (not "Schweiz")
- Spain = "ES" (not "España")

Return the information as JSON. The response should be in the following format:
{{
    "event": {{
        "name": "OCEANMAN Phuket 2024",
        "website": "https://oceanmanswim.com/phuket-thailand/",
        "date_start": "2024-07-15",
        "date_end": "2024-07-15",
        "location": {{
            "city": "Phuket",
            "country": "TH",
            "water_name": "Andaman Sea",
            "water_type": "sea",
            "address": "123 Beach Road, Phuket"
        }},
        "organizer": {{
            "name": "OCEANMAN"
        }},
        "needs_medical_certificate": true,
        "needs_license": false,
        "sold_out": false,
        "cancelled": false,
        "with_ranking": true,
        "water_temp": 28.5,
        "description": "This is a public description of the event."
    }},
    "races": [ {{
        "name": "10 km Open Water Race",
        "date": "2024-07-15",
        "race_time": "09:00:00",
        "distance": 10.0,
        "wetsuit": "optional",
        "price": {{
            "amount": 50.0,
            "currency": "EUR"
        }}
    }}]
}}

Do not return any comments in the JSON file! Return plain JSON.

Note: There are multiple races per swim event.
Please analyze all the URLs provided and combine the information to create the most complete event profile possible.
If some data is not found in any of the URLs, return null in the field.
For the wetsuit field, only use one of these values: 'compulsory', 'optional', 'prohibited'.
For the water_type field, only use one of these values: 'river', 'sea', 'lake', 'pool'.
For the country field, you MUST use 2-letter ISO 3166-1 alpha-2 codes in Latin letters (e.g., JP, DE, US, GB, FR, etc.).
"""

            response = agent.chat(prompt)

            # Extract JSON from response
            json_text = response.response
            json_match = re.search(r"```json\s*(.*?)\s*```", json_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)

            data = json.loads(json_text)
            return data

        except Exception as e:
            self.logger.error(f"Error extracting event data: {str(e)}")
            return None

    def _apply_updates(
        self, event: Event, event_data: Dict, urls: List[str], dry_run: bool
    ) -> bool:
        """
        Apply updates to the event while preserving location and organizer

        Returns: True if successful, False otherwise
        """
        try:
            from djmoney.money import Money

            new_event_data = event_data["event"]
            races_data = event_data.get("races", [])

            if dry_run:
                self.stdout.write(self.style.WARNING(f"[DRY RUN] Would update event:"))
                self.stdout.write(f"  Name: {new_event_data.get('name')}")
                self.stdout.write(f"  Dates: {new_event_data.get('date_start')} to {new_event_data.get('date_end')}")
                self.stdout.write(f"  Website: {new_event_data.get('website')}")
                self.stdout.write(f"  Races: {len(races_data)}")
                return True

            # Update event fields (preserve location and organizer)
            event.name = new_event_data.get("name", event.name)
            event.website = new_event_data.get("website", urls[0])
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

            # Update source
            event.source = f"Auto-updated from: {', '.join(urls)}"

            # Make visible but keep unverified
            event.invisible = False

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

            return True

        except Exception as e:
            self.logger.error(f"Error applying updates to event {event.id}: {str(e)}")
            return False

    def _append_internal_comment(self, event: Event, message: str, dry_run: bool):
        """Append a timestamped message to the event's internal comment"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"

        if dry_run:
            self.logger.info(f"[DRY RUN] Would append to internal_comment: {log_entry}")
            return

        if event.internal_comment:
            event.internal_comment = f"{event.internal_comment}\n{log_entry}"
        else:
            event.internal_comment = log_entry

        # Truncate if too long (field has max_length=2048)
        if len(event.internal_comment) > 2000:
            event.internal_comment = event.internal_comment[-2000:]

        event.save()
