from typing import List, Dict, Any, Set
from datetime import date
import logging

logger = logging.getLogger(__name__)


class URLUtils:
    """
    Utility class for URL operations like normalization and checking for existing URLs.
    Used by both discover_event_urls.py and crawl_events.py.
    """

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL for comparison"""
        # Remove protocol
        url = url.split("://")[-1]

        # Remove trailing slash
        if url.endswith("/"):
            url = url[:-1]

        # Remove www.
        if url.startswith("www."):
            url = url[4:]

        return url.lower()

    @classmethod
    def filter_existing_urls(
        cls, urls: List[Dict[str, Any]], stdout=None, stderr=None
    ) -> List[Dict[str, Any]]:
        """
        Filter out URLs that already have a future event in the database.
        URLs with only past events are NOT filtered (they may have a new edition).
        """
        from app.models import Event

        new_urls = []
        today = date.today()

        try:
            # Fetch only future visible events
            # (we want to allow re-crawling past events and hidden/copied events)
            if stdout:
                stdout.write("Fetching future visible events from database...")
            future_events = list(
                Event.objects.filter(date_start__gte=today, invisible=False)
            )
            if stdout:
                stdout.write(f"Found {len(future_events)} future visible events in database")

            # Create a set of normalized website URLs for future events only
            existing_urls = set()
            for event in future_events:
                if event.website:
                    existing_urls.add(cls.normalize_url(event.website))

            if stdout:
                stdout.write(
                    f"Found {len(existing_urls)} unique website URLs with future visible events"
                )

            # Filter URLs
            for url_data in urls:
                url = url_data["url"]
                normalized_url = cls.normalize_url(url)

                # Check if this URL has a future event in the database
                has_future_event = False
                for existing_url in existing_urls:
                    if existing_url in normalized_url or normalized_url in existing_url:
                        has_future_event = True
                        break

                if not has_future_event:
                    new_urls.append(url_data)

        except Exception as e:
            # If database access fails, log the error and return all URLs
            error_msg = f"Database access failed, skipping database filtering: {str(e)}"
            if stderr:
                stderr.write(error_msg)
            else:
                logger.warning(error_msg)

            warning_msg = "Continuing without filtering against database. All URLs will be treated as new."
            if stdout:
                stdout.write(warning_msg)
            else:
                logger.warning(warning_msg)

            return urls

        return new_urls

    @classmethod
    def filter_existing_url_sets(
        cls, url_sets: List[List[str]], stdout=None, stderr=None
    ) -> List[List[str]]:
        """
        Filter out URL sets that already have a future event in the database.
        URLs with only past events are NOT filtered (they may have a new edition).
        """
        from app.models import Event

        new_url_sets = []
        today = date.today()

        try:
            # Fetch only future visible events
            # (we want to allow re-crawling past events and hidden/copied events)
            if stdout:
                stdout.write("Fetching future visible events from database...")
            future_events = list(
                Event.objects.filter(date_start__gte=today, invisible=False)
            )
            if stdout:
                stdout.write(f"Found {len(future_events)} future visible events in database")

            # Create a set of normalized website URLs for future events only
            existing_urls = set()
            for event in future_events:
                if event.website:
                    existing_urls.add(cls.normalize_url(event.website))

            if stdout:
                stdout.write(
                    f"Found {len(existing_urls)} unique website URLs with future visible events"
                )

            # Filter URL sets
            for urls in url_sets:
                # Check if any URL in this set has a future event in the database
                has_future_event = False
                for url in urls:
                    normalized_url = cls.normalize_url(url)
                    for existing_url in existing_urls:
                        if (
                            existing_url in normalized_url
                            or normalized_url in existing_url
                        ):
                            has_future_event = True
                            if stdout:
                                stdout.write(f"Skipping URL (future event exists): {url}")
                            break
                    if has_future_event:
                        break

                if not has_future_event:
                    new_url_sets.append(urls)

        except Exception as e:
            # If database access fails, log the error and return all URLs
            error_msg = f"Database access failed, skipping database filtering: {str(e)}"
            if stderr:
                stderr.write(error_msg)
            else:
                logger.warning(error_msg)

            warning_msg = "Continuing without filtering against database. All URL sets will be treated as new."
            if stdout:
                stdout.write(warning_msg)
            else:
                logger.warning(warning_msg)

            return url_sets

        if stdout:
            stdout.write(
                f"After filtering, {len(new_url_sets)} of {len(url_sets)} URL sets remain to be processed"
            )

        return new_url_sets
