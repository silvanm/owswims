import logging
from datetime import date
from typing import Any, Dict, List, Optional

from django.conf import settings
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Filter,
    FilterExpression,
    Metric,
    RunReportRequest,
)

logger = logging.getLogger(__name__)


class GoogleAnalyticsService:
    """
    Service for fetching Google Analytics 4 data.
    Uses the Google Analytics Data API v1beta.
    """

    def __init__(
        self,
        property_id: Optional[str] = None,
        stdout=None,
        stderr=None,
    ):
        """
        Initialize the Google Analytics service.

        Args:
            property_id: GA4 property ID (defaults to settings.GA_PROPERTY_ID)
            stdout: Output stream for logging (optional)
            stderr: Error stream for logging (optional)

        Note: Uses GOOGLE_APPLICATION_CREDENTIALS env var for authentication.
        """
        self.property_id = property_id or getattr(settings, "GA_PROPERTY_ID", "")
        self.stdout = stdout
        self.stderr = stderr
        self._client = None

    def _get_client(self) -> BetaAnalyticsDataClient:
        """Lazy initialization of the Analytics client using default credentials."""
        if self._client is None:
            # Uses GOOGLE_APPLICATION_CREDENTIALS env var
            self._client = BetaAnalyticsDataClient()
        return self._client

    def _log(self, msg: str, level: str = "info", style_func=None):
        """Log a message to both the logger and command output if available."""
        getattr(logger, level)(msg)

        if level in ["warning", "error"] and self.stderr:
            if style_func:
                self.stderr.write(style_func(msg))
            else:
                self.stderr.write(msg)
        elif self.stdout:
            if style_func:
                self.stdout.write(style_func(msg))
            else:
                self.stdout.write(msg)

    def fetch_page_active_users(
        self,
        year: int,
        page_path_filter: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        Fetch active user counts grouped by page path for a specific year.

        Args:
            year: The year to fetch data for (e.g., 2025)
            page_path_filter: Optional filter for page paths
                            (e.g., "/event/" to only get event pages)

        Returns:
            Dictionary mapping page paths to active user counts
            Example: {"/en/event/lake-annecy-2025/": 150, ...}
        """
        if not self.property_id:
            self._log("GA_PROPERTY_ID not configured", "error")
            return {}

        try:
            client = self._get_client()

            # Date range for the entire year
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)

            # Build the request
            request_params = {
                "property": f"properties/{self.property_id}",
                "date_ranges": [
                    DateRange(
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                    )
                ],
                "dimensions": [Dimension(name="pagePath")],
                "metrics": [Metric(name="activeUsers")],
                "limit": 10000,
            }

            # Add page path filter if specified
            if page_path_filter:
                request_params["dimension_filter"] = FilterExpression(
                    filter=Filter(
                        field_name="pagePath",
                        string_filter=Filter.StringFilter(
                            match_type=Filter.StringFilter.MatchType.CONTAINS,
                            value=page_path_filter,
                        ),
                    )
                )

            request = RunReportRequest(**request_params)
            response = client.run_report(request)

            page_stats = {}
            for row in response.rows:
                page_path = row.dimension_values[0].value
                active_users = int(row.metric_values[0].value)
                page_stats[page_path] = active_users

            self._log(f"Fetched {len(page_stats)} page stats from GA4 for {year}")
            return page_stats

        except Exception as e:
            self._log(f"Error fetching GA4 data: {str(e)}", "error")
            return {}

    def match_events_to_analytics(
        self,
        page_stats: Dict[str, int],
        events: List[Any],
    ) -> Dict[int, int]:
        """
        Match GA4 page statistics to events by slug.

        Args:
            page_stats: Dictionary of page paths to active user counts
            events: List of Event objects with slug field

        Returns:
            Dictionary mapping event IDs to active user counts
        """
        event_stats = {}

        for event in events:
            if not event.slug:
                continue

            # Sum up all pages containing this event's slug
            # This handles multiple language paths (/en/event/slug/, /de/event/slug/)
            total_users = 0
            matched_paths = []

            for page_path, user_count in page_stats.items():
                if event.slug in page_path:
                    total_users += user_count
                    matched_paths.append(page_path)

            if total_users > 0:
                event_stats[event.id] = total_users
                self._log(
                    f"  Event {event.id} ({event.slug}): {total_users} users "
                    f"from {len(matched_paths)} page(s)"
                )

        self._log(f"Matched {len(event_stats)} events to analytics data")
        return event_stats
