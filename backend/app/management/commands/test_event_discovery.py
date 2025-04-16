import os
import json
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from llama_index.llms.openai import OpenAI
from app.services.scraping_service import ScrapingService

from .discover_event_urls import serper


class Command(BaseCommand):
    help = "Test the event discovery system with minimal parameters"

    def add_arguments(self, parser):
        parser.add_argument(
            "--keyword", type=str, help="Test keyword search with a specific term"
        )
        parser.add_argument(
            "--url", type=str, help="Test URL validation with a specific URL"
        )
        parser.add_argument(
            "--firecrawl-api-key",
            type=str,
            help="FireCrawl API key (falls back to FIRECRAWL_API_KEY env var)",
        )

    def handle(self, *args, **options):
        # Check for required environment variables
        if not os.environ.get("OPENAI_API_KEY"):
            raise CommandError("OPENAI_API_KEY environment variable is required")

        firecrawl_api_key = options.get("firecrawl_api_key") or os.environ.get(
            "FIRECRAWL_API_KEY"
        )
        if not firecrawl_api_key:
            raise CommandError(
                "FireCrawl API key is required (use --firecrawl-api-key or set FIRECRAWL_API_KEY env var)"
            )

        # Initialize scraping service
        scraping_service = ScrapingService(api_key=firecrawl_api_key)

        # Test keyword search
        keyword = options.get("keyword")
        if keyword:
            self._test_search(keyword)

        # Test URL validation
        url = options.get("url")
        if url:
            self._test_url_validation(url, scraping_service)

        # If no specific test was requested
        if not keyword and not url:
            self.stdout.write(
                "No test specified. Use --keyword or --url to run specific tests."
            )

    def _test_search(self, keyword):
        """Test search functionality"""
        self.stdout.write(f"Testing search with keyword: {keyword}")

        try:
            # Execute the search
            result = serper(keyword)
            data = json.loads(result)

            # Display results
            self.stdout.write(
                self.style.SUCCESS(f"Found {len(data.get('organic', []))} results")
            )
            for idx, item in enumerate(data.get("organic", [])[:5], 1):
                self.stdout.write(f"{idx}. {item.get('title')}")
                self.stdout.write(f"   URL: {item.get('link')}")
                self.stdout.write("")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during search test: {str(e)}"))

    def _test_url_validation(self, url, scraping_service):
        """Test URL validation with GPT"""
        self.stdout.write(f"Testing URL validation for: {url}")

        try:
            # Scrape the content
            self.stdout.write("Scraping content...")
            content = scraping_service.scrape(url)

            if not content:
                self.stderr.write(self.style.ERROR("Failed to scrape content"))
                return

            self.stdout.write(self.style.SUCCESS("Successfully scraped content"))
            self.stdout.write(f"Content length: {len(content)} characters")

            # Create a prompt for the model
            self.stdout.write(f"Validating with {settings.OPENAI_MODEL}...")
            prompt = f"""
            Analyze this webpage content and determine if it's an open water swimming event website.
            
            Content:
            {content[:4000]}  # Limit content length
            
            Answer with YES or NO, followed by a brief explanation.
            Only answer YES if this is clearly a page for a specific open water swimming event or a directory of such events.
            """

            # Call a smaller model variant for faster and less expensive validation
            mini_model = (
                f"{settings.OPENAI_MODEL}-mini"
                if "-mini" not in settings.OPENAI_MODEL
                else settings.OPENAI_MODEL
            )
            llm = OpenAI(model=mini_model)
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
