import logging
import os
import dotenv
from django.conf import settings
from django.utils import timezone
from django.core.management.base import OutputWrapper
from io import StringIO

from .services.event_processor import EventProcessor
from .services.event_crawler import EventCrawler
from .management.commands.crawl_events import Command as CrawlEventsCommand

logger = logging.getLogger(__name__)


def crawl_single_event_async(url, dry_run=False):
    """
    Crawl a single event asynchronously using Django Q.
    This is equivalent to running: python manage.py crawl_events --event 'URL'

    Args:
        url (str): URL of the event to crawl
        dry_run (bool): Whether to perform a dry run without saving to the database

    Returns:
        str: Result message
    """
    logger.info(f"Starting asynchronous crawling of event: {url}")

    # Create a string buffer to capture output
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    stdout_wrapper = OutputWrapper(stdout_buffer)
    stderr_wrapper = OutputWrapper(stderr_buffer)

    try:
        # Load environment variables
        dotenv.load_dotenv()
        api_key = os.environ.get("FIRECRAWL_API_KEY")

        if not api_key:
            return "Error: FIRECRAWL_API_KEY environment variable not set"

        # Initialize the command
        command = CrawlEventsCommand()
        command.stdout = stdout_wrapper
        command.stderr = stderr_wrapper

        # Initialize the event processor
        processor = EventProcessor(
            firecrawl_api_key=api_key,
            stdout=stdout_wrapper,
            stderr=stderr_wrapper,
            dry_run=dry_run,
        )

        # Process the event
        result = command._process_single_event(processor, [url])

        # Capture the output
        stdout_output = stdout_buffer.getvalue()
        stderr_output = stderr_buffer.getvalue()

        # Create result message
        if result:
            message = f"Successfully processed event from URL: {url}"
            logger.info(message)
        else:
            message = f"Failed to process event from URL: {url}"
            logger.warning(message)

        # Include output in result
        if stdout_output:
            message += f"\n\nOutput:\n{stdout_output}"
        if stderr_output:
            message += f"\n\nErrors:\n{stderr_output}"

        return message

    except Exception as e:
        error_msg = f"Error crawling event: {str(e)}"
        logger.error(error_msg)
        return error_msg


def verify_locations_async(location_ids=None, limit=None, dry_run=False):
    """
    Verify locations asynchronously using Django Q.

    Args:
        location_ids (list): List of location IDs to verify, or None for all unverified
        limit (int): Maximum number of locations to process
        dry_run (bool): Whether to perform a dry run without saving to the database

    Returns:
        str: Result message
    """
    from .models import Location
    from .management.commands.process_unverified_locations import (
        Command as LocationProcessor,
    )

    logger.info(f"Starting asynchronous location verification")

    # Create a string buffer to capture output
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    stdout_wrapper = OutputWrapper(stdout_buffer)
    stderr_wrapper = OutputWrapper(stderr_buffer)

    try:
        # Initialize the location processor
        processor = LocationProcessor()
        processor.stdout = stdout_wrapper
        processor.stderr = stderr_wrapper

        # Get locations to process
        if location_ids:
            locations = Location.objects.filter(id__in=location_ids)
            logger.info(f"Processing {len(locations)} specified locations")
        else:
            locations = Location.objects.filter(verified_at__isnull=True)
            if limit:
                locations = locations[:limit]
            logger.info(f"Processing {len(locations)} unverified locations")

        # Process each location
        processed_count = 0
        verified_count = 0

        for location in locations:
            if not dry_run:
                # Process the location
                processed = processor.process_location(location)
                if processed:
                    processed_count += 1

                    # Verify the location
                    location.verified_at = timezone.now()
                    location.save()
                    verified_count += 1
            else:
                # Just log in dry run mode
                logger.info(
                    f"[DRY RUN] Would process location: {location.city}, {location.country}"
                )
                processed_count += 1

        # Capture the output
        stdout_output = stdout_buffer.getvalue()
        stderr_output = stderr_buffer.getvalue()

        # Create result message
        result = f"Processed {processed_count} locations, verified {verified_count}"
        if dry_run:
            result = f"[DRY RUN] {result}"

        logger.info(result)

        # Include output in result
        if stdout_output:
            result += f"\n\nOutput:\n{stdout_output}"
        if stderr_output:
            result += f"\n\nErrors:\n{stderr_output}"

        return result

    except Exception as e:
        error_msg = f"Error verifying locations: {str(e)}"
        logger.error(error_msg)
        return error_msg
