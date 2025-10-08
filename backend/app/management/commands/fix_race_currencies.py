import csv
import logging
import os
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from djmoney.money import Money
from app.models import Event, Race

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fix currencies for future events based on country codes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without making changes to the database",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output",
        )
        parser.add_argument(
            "--us-only",
            action="store_true",
            help="Only process US events",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        verbose = options.get("verbose", False)
        us_only = options.get("us_only", False)

        # Configure logging
        log_level = logging.INFO if verbose else logging.WARNING
        logger.setLevel(log_level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Load country to currency mapping
        country_to_currency = self._load_country_currency_mapping()
        if not country_to_currency:
            self.stdout.write(
                self.style.ERROR("Failed to load country-to-currency mapping")
            )
            return

        self.stdout.write(
            f"Loaded {len(country_to_currency)} country-currency mappings"
        )

        # Get future events (events with date_start >= today)
        today = datetime.now().date()
        future_events = Event.objects.filter(date_start__gte=today)

        # Filter for US events only if specified
        if us_only:
            future_events = future_events.filter(location__country="US")
            self.stdout.write(f"Found {future_events.count()} future US events")
        else:
            self.stdout.write(f"Found {future_events.count()} future events")

        # Process each event
        total_races = 0
        updated_races = 0
        failed_races = 0

        for event in future_events:
            location = event.location
            country_code = location.country if location else None

            if not country_code:
                logger.warning(f"Event {event.id} ({event.name}) has no country code")
                continue

            # Get the appropriate currency for this country
            currency = country_to_currency.get(country_code)

            if not currency:
                logger.warning(
                    f"No currency mapping found for country code {country_code}"
                )
                continue

            # Get races for this event with EUR currency
            races = Race.objects.filter(event=event, price_currency="EUR").exclude(
                price__isnull=True
            )

            if not races:
                if verbose:
                    logger.info(
                        f"Event {event.id} ({event.name}) in {country_code} has no races with EUR currency"
                    )
                continue

            logger.info(
                f"Processing event {event.id} ({event.name}) in {country_code}, currency={currency}"
            )

            # Update race currencies
            for race in races:
                total_races += 1

                if dry_run:
                    logger.info(
                        f"[DRY RUN] Would update race {race.id} ({race.name}) price from "
                        f"{race.price.amount} EUR to {race.price.amount} {currency}"
                    )
                    updated_races += 1
                else:
                    try:
                        # Create a new Money object with the same amount but different currency
                        race.price = Money(race.price.amount, currency)
                        race.save()
                        updated_races += 1
                        logger.info(
                            f"Updated race {race.id} ({race.name}) price from "
                            f"{race.price.amount} EUR to {race.price.amount} {currency}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to update race {race.id} ({race.name}): {str(e)}"
                        )
                        failed_races += 1

        # Print summary
        self.stdout.write(self.style.SUCCESS(f"Processed {total_races} races"))
        self.stdout.write(self.style.SUCCESS(f"Updated {updated_races} races"))
        if failed_races:
            self.stdout.write(
                self.style.ERROR(f"Failed to update {failed_races} races")
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "This was a dry run - no changes were made to the database"
                )
            )

    def _load_country_currency_mapping(self):
        """Load country code to currency code mapping from CSV file"""
        csv_path = os.path.join(
            settings.BASE_DIR,
            "app",
            "data",
            "country-code-to-currency-code-mapping.csv",
        )

        if not os.path.exists(csv_path):
            self.stderr.write(f"Mapping file not found: {csv_path}")
            return {}

        country_to_currency = {}

        try:
            with open(csv_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    country_code = row.get("CountryCode")
                    currency_code = row.get("Code")

                    if country_code and currency_code:
                        country_to_currency[country_code] = currency_code
        except Exception as e:
            self.stderr.write(f"Error reading mapping file: {str(e)}")
            return {}

        return country_to_currency
