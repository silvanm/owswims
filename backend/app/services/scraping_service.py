import logging
from firecrawl import FirecrawlApp
from django.core.management.base import OutputWrapper

logger = logging.getLogger(__name__)


class ScrapingService:
    """Service for web scraping using Firecrawl"""

    def __init__(
        self, api_key: str, stdout: OutputWrapper = None, stderr: OutputWrapper = None
    ):
        self.firecrawl_app = FirecrawlApp(api_key=api_key)
        self.stdout = stdout
        self.stderr = stderr

    def _log(self, msg: str, level: str = "info", style_func=None):
        """Log a message to both the logger and command output if available"""
        # Log to Python logger
        getattr(logger, level)(msg)

        # Log to command output if available
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

    def scrape(self, url: str, profile=None) -> str:
        """
        Scrape a webpage and return its content.
        Uses Firecrawl with optimized settings for event pages.

        Args:
            url: The URL to scrape
            profile: Optional crawl profile with actions to perform before scraping
        """
        try:
            params = {
                "formats": ["markdown"],
                "excludeTags": [
                    "script",
                    "style",
                    "svg",
                    "iframe",
                    "nav",
                    "footer",
                    "header",
                ],
                "waitFor": 1000,
            }

            # Add actions from profile if available
            if profile and "actions" in profile:
                params["actions"] = profile["actions"]
                self._log(
                    f"Using crawl profile '{profile.get('name', 'unnamed')}' for {url}"
                )

            scrape_result = self.firecrawl_app.scrape_url(url, params=params)
            return scrape_result["markdown"]
        except Exception as e:
            self._log(f"Failed to scrape {url}: {str(e)}", "error")
            return ""
