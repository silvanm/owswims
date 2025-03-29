import os
import json
from django.core.management.base import BaseCommand
from llama_index.llms.openai import OpenAI

from app.services.scraping_service import ScrapingService
from .discover_event_urls import serper


class Command(BaseCommand):
    help = "Test the event discovery system with minimal parameters"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keyword",
            type=str,
            default="open water swimming Switzerland 2025",
            help="Test search keyword",
        )
        parser.add_argument(
            "--url",
            type=str,
            help="Test URL to validate (skips search if provided)",
        )

    def handle(self, *args, **options):
        # Check for required environment variables
        required_env_vars = ["OPENAI_API_KEY", "SERPER_API_KEY", "FIRECRAWL_API_KEY"]
        missing_vars = [var for var in required_env_vars if var not in os.environ]
        if missing_vars:
            self.stderr.write(
                self.style.ERROR(
                    f"Missing required environment variables: {', '.join(missing_vars)}"
                )
            )
            return

        # Initialize services
        scraping_service = ScrapingService(
            api_key=os.environ["FIRECRAWL_API_KEY"],
            stdout=self.stdout,
            stderr=self.stderr,
        )

        # Test URL validation if provided
        if options.get("url"):
            self._test_url_validation(options["url"], scraping_service)
            return

        # Otherwise test search
        self._test_search(options["keyword"])

    def _test_search(self, keyword):
        """Test the Google Search functionality"""
        self.stdout.write(self.style.SUCCESS(f"Testing search with keyword: {keyword}"))

        try:
            # Execute search
            self.stdout.write("Executing Google search...")
            result = serper(keyword)
            data = json.loads(result)

            # Display results
            self.stdout.write(self.style.SUCCESS("Search results:"))

            if "organic" in data:
                for i, item in enumerate(data["organic"], 1):
                    self.stdout.write(f"\n{i}. {item.get('title', 'No title')}")
                    self.stdout.write(f"   URL: {item.get('link', 'No link')}")
                    self.stdout.write(
                        f"   Snippet: {item.get('snippet', 'No snippet')}"
                    )
            else:
                self.stdout.write(self.style.WARNING("No organic results found"))

            # Suggest next steps
            self.stdout.write("\nTo test URL validation, run:")
            if "organic" in data and len(data["organic"]) > 0:
                example_url = data["organic"][0].get("link", "https://example.com")
                self.stdout.write(
                    f'python manage.py test_event_discovery --url "{example_url}"'
                )
            else:
                self.stdout.write(
                    'python manage.py test_event_discovery --url "https://example.com"'
                )

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during search test: {str(e)}"))

    def _test_url_validation(self, url, scraping_service):
        """Test the URL validation functionality"""
        self.stdout.write(self.style.SUCCESS(f"Testing URL validation with: {url}"))

        try:
            # Scrape the webpage content
            self.stdout.write("Scraping webpage content...")
            content = scraping_service.scrape(url)

            if not content:
                self.stderr.write(self.style.ERROR("Failed to scrape content"))
                return

            self.stdout.write(self.style.SUCCESS("Successfully scraped content"))
            self.stdout.write(f"Content length: {len(content)} characters")

            # Create a prompt for GPT-4o
            self.stdout.write("Validating with GPT-4o...")
            prompt = f"""
            Analyze this webpage content and determine if it's an open water swimming event website.
            
            Content:
            {content[:4000]}  # Limit content length
            
            Answer with YES or NO, followed by a brief explanation.
            Only answer YES if this is clearly a page for a specific open water swimming event or a directory of such events.
            """

            # Call GPT-4o-mini for faster and less expensive validation
            llm = OpenAI(model="gpt-4o-mini")
            response = llm.complete(prompt)

            # Convert the response to a string
            response_text = str(response)

            # Display result
            self.stdout.write(self.style.SUCCESS("Validation result:"))
            self.stdout.write(response_text)

            # Parse the response
            is_event_site = response_text.lower().startswith("yes")
            if is_event_site:
                self.stdout.write(
                    self.style.SUCCESS("This URL was identified as an event website")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "This URL was NOT identified as an event website"
                    )
                )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error during URL validation test: {str(e)}")
            )
