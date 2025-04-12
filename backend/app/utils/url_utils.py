from typing import List, Dict, Any, Set
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
        """Filter out URLs that are already in the database"""
        from app.models import Event

        new_urls = []

        try:
            # Fetch all events once
            if stdout:
                stdout.write("Fetching all events from database...")
            all_events = list(Event.objects.all())
            if stdout:
                stdout.write(f"Found {len(all_events)} events in database")

            # Create a set of normalized website URLs for faster lookup
            existing_urls = set()
            for event in all_events:
                if event.website:
                    existing_urls.add(cls.normalize_url(event.website))

            if stdout:
                stdout.write(
                    f"Found {len(existing_urls)} unique website URLs in database"
                )

            # Filter URLs
            for url_data in urls:
                url = url_data["url"]
                normalized_url = cls.normalize_url(url)

                # Check if this URL exists in the database
                exists = False
                for existing_url in existing_urls:
                    if existing_url in normalized_url or normalized_url in existing_url:
                        exists = True
                        break

                if not exists:
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
        """Filter out URL sets that already exist in the database"""
        from app.models import Event

        new_url_sets = []

        try:
            # Fetch all events once
            if stdout:
                stdout.write("Fetching all events from database...")
            all_events = list(Event.objects.all())
            if stdout:
                stdout.write(f"Found {len(all_events)} events in database")

            # Create a set of normalized website URLs for faster lookup
            existing_urls = set()
            for event in all_events:
                if event.website:
                    existing_urls.add(cls.normalize_url(event.website))

            if stdout:
                stdout.write(
                    f"Found {len(existing_urls)} unique website URLs in database"
                )

            # Filter URL sets
            for urls in url_sets:
                # Check if any URL in this set exists in the database
                exists = False
                for url in urls:
                    normalized_url = cls.normalize_url(url)
                    for existing_url in existing_urls:
                        if (
                            existing_url in normalized_url
                            or normalized_url in existing_url
                        ):
                            exists = True
                            if stdout:
                                stdout.write(f"Skipping existing URL: {url}")
                            break
                    if exists:
                        break

                if not exists:
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
