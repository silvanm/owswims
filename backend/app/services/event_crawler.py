import logging
import re
import urllib.parse
from typing import List, Dict, Any, Set, Tuple, Optional
from django.core.management.base import OutputWrapper
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

from .scraping_service import ScrapingService


logger = logging.getLogger(__name__)


class EventCrawler:
    """
    Crawler that finds swimming event URLs from directory websites.

    This class is responsible for:
    1. Finding event URLs from swimming event websites (get_event_urls method)
       - Discovers and extracts URLs for swimming events from directory websites
       - Groups related URLs for the same event together
       - Filters events by location and date
    """

    def __init__(
        self,
        firecrawl_api_key: str,
        stdout: OutputWrapper = None,
        stderr: OutputWrapper = None,
        profile=None,
    ):
        self.scraping_service = ScrapingService(
            api_key=firecrawl_api_key, stdout=stdout, stderr=stderr
        )
        self.llm = OpenAI(model="gpt-4o")
        self.profile = profile

        # Cache for scraped pages to avoid re-scraping
        self.page_cache = {}

    def get_event_urls(self, start_url: str) -> List[List[str]]:
        """
        Get lists of event URLs from the starting URL.
        Returns a list of URL lists, where each inner list contains URLs for the same event
        (e.g. registration page and event info page)
        """

        # Create a tool for the LLM to scrape additional pages if needed
        # If a profile is available, use it for scraping
        def scrape_with_profile(url: str) -> str:
            return self.scraping_service.scrape(url, profile=self.profile)

        scrape_tool = FunctionTool.from_defaults(fn=scrape_with_profile)
        agent = ReActAgent.from_tools(
            [scrape_tool], max_iterations=10, llm=self.llm, verbose=True
        )

        # Get current date for filtering future events
        from datetime import datetime

        current_date = datetime.now().strftime("%Y-%m-%d")

        # Check if a custom prompt is provided in the profile
        if self.profile and "custom_prompt" in self.profile:
            # Use the custom prompt from the profile
            # Replace placeholders with actual values
            prompt = (
                self.profile["custom_prompt"]
                .replace("{start_url}", start_url)
                .replace("{current_date}", current_date)
            )
            logger.info(
                f"Using custom prompt from profile '{self.profile.get('name', 'unnamed')}'"
            )
        else:
            # Use the default prompt
            prompt = f"""Visit this URL and find all open water swimming events: {start_url}
Please analyze the page and find URLs for all swimming events. Some events might have multiple URLs 
(e.g. a registration page and an info page).

Today's date is {current_date}. Only include events that will take place in the future (after today's date).

It's sufficient just to extract the URLs. Extracting event names and locations is not your responsibility.

Return the information as JSON in the following format:
{{
    "events": [
        {{
            "urls": ["https://event1-info.com", "https://event1-registration.com"],
            "name": "Event 1 name",  // optional, for logging
            "location": "Paris, France"  // optional, for filtering
        }},
        {{
            "urls": ["https://event2.com"],
            "name": "Event 2 name",  // optional, for logging
            "location": "Barcelona, Spain"  // optional, for filtering
        }}
    ]
}}

Make sure to:
1. Only include URLs that lead to specific event pages
2. Group URLs that belong to the same event together. If two entries are on the same date and 
   the same location, you can assume that they are the same event.
3. Include both info pages and registration pages when available
4. Follow pagination or "Load More" links if present
5. Make URLs absolute, not relative
6. Only include URLs from the same domain or known registration platforms
8. Only include future events (after {current_date})

"""

        response = agent.chat(prompt)
        try:
            # Extract JSON from the response
            import json
            import re

            json_match = re.search(r"\{[\s\S]*\}", response.response)
            if not json_match:
                logger.error("No JSON found in LLM response")
                return []

            json_str = json_match.group(0)
            data = json.loads(json_str)

            # Extract and validate URL lists
            url_lists = []
            for event in data.get("events", []):
                urls = event.get("urls", [])
                name = event.get("name", "Unknown Event")

                # Validate URLs
                valid_urls = []
                for url in urls:
                    # Basic URL validation
                    if not url.startswith(("http://", "https://")):
                        logger.warning(f"Skipping invalid URL for {name}: {url}")
                        continue
                    valid_urls.append(url)

                if valid_urls:
                    logger.info(
                        f"Found event: {name} with URLs: {', '.join(valid_urls)}"
                    )
                    url_lists.append(valid_urls)
                else:
                    logger.warning(f"No valid URLs found for event: {name}")

            return url_lists

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
            logger.debug(f"Response was: {response.response}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error processing LLM response: {str(e)}")
            logger.debug(f"Response was: {response.response}")
            return []
