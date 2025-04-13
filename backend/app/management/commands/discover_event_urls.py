from enum import Enum
import os
import json
import http.client
from typing import List, Dict, Any
import dotenv
from django.core.management.base import BaseCommand
from llama_index.llms.openai import OpenAI

from app.models import Event
from app.services.scraping_service import ScrapingService
from app.utils.url_utils import URLUtils


class EventType(Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"
    UNKNOWN = "unknown"


def serper(keyword: str, country_code: str = "ch", language: str = "en"):
    """Search for a keyword on Google and return the first result"""
    conn = http.client.HTTPSConnection("google.serper.dev")

    # Convert country code to lowercase for Serper API
    gl = country_code.lower()

    # Use the provided language code
    hl = language.lower()

    payload = json.dumps({"q": keyword, "gl": gl, "hl": hl, "num": 40})
    headers = {
        "X-API-KEY": os.environ["SERPER_API_KEY"],
        "Content-Type": "application/json",
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data


class Command(BaseCommand):
    help = "Discover new event URLs using Google Search and GPT-4o validation"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit the number of search queries to execute",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="discovered_event_urls.json",
            help="Output file for discovered URLs",
        )
        parser.add_argument(
            "--cache",
            type=str,
            default="url_validation_cache.json",
            help="Cache file for URL validation results",
        )
        parser.add_argument(
            "--countries",
            nargs="+",
            type=str,
            help="Limit search to specific countries (country codes)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without saving to file",
        )

    def handle(self, *args, **options):
        dotenv.load_dotenv()

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

        # Get output and cache file paths
        output_file = options.get("output")
        cache_file = options.get("cache")
        dry_run = options.get("dry_run", False)

        # Load validation cache
        validation_cache = self.load_validation_cache(cache_file)
        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {len(validation_cache)} cached validation results"
            )
        )

        # Load existing valid URLs if the output file exists
        valid_urls = self.load_existing_valid_urls(output_file) if not dry_run else []
        if valid_urls:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Loaded {len(valid_urls)} existing valid URLs from {output_file}"
                )
            )

        # 1. Generate keywords with GPT-4o
        self.stdout.write("Generating keywords with GPT-4o...")
        keywords = self.generate_keywords()
        self.stdout.write(self.style.SUCCESS(f"Generated {len(keywords)} keywords"))

        # 2. Define country-language pairs
        country_languages = self.get_country_languages(options.get("countries"))
        self.stdout.write(
            self.style.SUCCESS(f"Using {len(country_languages)} countries for search")
        )

        # 3. Translate keywords to local languages
        self.stdout.write("Translating keywords to local languages...")
        translated_keywords = self.translate_keywords(keywords, country_languages)

        # 4. Generate search queries
        self.stdout.write("Generating search queries...")
        search_queries = self.generate_search_queries(
            keywords, translated_keywords, country_languages
        )

        # Apply limit if specified
        limit = options.get("limit")
        if limit and limit > 0:
            original_count = len(search_queries)
            search_queries = search_queries[:limit]
            self.stdout.write(
                self.style.WARNING(
                    f"Limiting to {limit} search queries (from {original_count} total)"
                )
            )

        # 5. Execute Google searches
        self.stdout.write("Executing Google searches...")
        all_urls = []
        for i, query in enumerate(search_queries, 1):
            self.stdout.write(f"Searching ({i}/{len(search_queries)}): {query}")
            urls = self.search_for_events(query)
            all_urls.extend(urls)
            self.stdout.write(f"  Found {len(urls)} potential URLs")

        self.stdout.write(
            self.style.SUCCESS(
                f"Found {len(all_urls)} total potential URLs from all searches"
            )
        )

        # 6. Filter results against database and already processed URLs
        self.stdout.write("Filtering out URLs already in database or processed...")
        new_urls = URLUtils.filter_existing_urls(
            all_urls, stdout=self.stdout, stderr=self.stderr
        )

        # Also filter out URLs that are already in the validation cache
        new_urls = [
            url_data
            for url_data in new_urls
            if URLUtils.normalize_url(url_data["url"]) not in validation_cache
        ]

        # Also filter out URLs that are already in the valid_urls list
        existing_valid_urls = {
            URLUtils.normalize_url(url_data["url"]) for url_data in valid_urls
        }
        new_urls = [
            url_data
            for url_data in new_urls
            if URLUtils.normalize_url(url_data["url"]) not in existing_valid_urls
        ]

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(new_urls)} new URLs to process")
        )

        # 7. Validate URLs with GPT-4o
        self.stdout.write("Validating URLs with GPT-4o...")
        newly_valid_urls = []

        for i, url_data in enumerate(new_urls, 1):
            url = url_data["url"]
            normalized_url = URLUtils.normalize_url(url)
            self.stdout.write(f"Validating ({i}/{len(new_urls)}): {url}")

            # Check if URL is already in the validation cache
            if normalized_url in validation_cache:
                cached_result = validation_cache[normalized_url]
                is_valid = cached_result["is_valid"]
                explanation = cached_result["explanation"]
                event_type = cached_result["event_type"]
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Using cached result: {explanation} (Type: {event_type})"
                    )
                )
            else:
                # Validate the URL
                is_valid, event_type, explanation = self.validate_url_with_gpt(
                    url_data, scraping_service
                )

                # Add to validation cache
                validation_cache[normalized_url] = {
                    "is_valid": is_valid,
                    "explanation": explanation,
                    "event_type": str(event_type.value),  # Convert enum to string
                    "url": url,
                    "title": url_data.get("title", ""),
                    "snippet": url_data.get("snippet", ""),
                    "query": url_data.get("query", ""),
                }

                # Save the cache after each validation to avoid losing results on interruption
                if not dry_run:
                    self.save_validation_cache(validation_cache, cache_file)

            if is_valid:
                url_data["validation"] = explanation
                url_data["event_type"] = (
                    event_type if isinstance(event_type, str) else str(event_type.value)
                )
                newly_valid_urls.append(url_data)
                valid_urls.append(url_data)
                self.stdout.write(
                    self.style.SUCCESS(f"  Valid: {explanation} (Type: {event_type})")
                )

                # Save valid URLs incrementally to avoid losing results on interruption
                if not dry_run:
                    self.save_urls_to_file(valid_urls, output_file)
            else:
                self.stdout.write(self.style.WARNING(f"  Invalid: {explanation}"))

        self.stdout.write(
            self.style.SUCCESS(f"Found {len(newly_valid_urls)} new valid event URLs")
        )

        # 8. Final save of valid URLs to file
        if not dry_run:
            self.save_urls_to_file(valid_urls, output_file)
            self.stdout.write(
                self.style.SUCCESS(f"Saved {len(valid_urls)} URLs to {output_file}")
            )
        else:
            self.stdout.write(self.style.WARNING("Dry run - not saving URLs to file"))

        # Display summary
        self.stdout.write("\nSummary:")
        self.stdout.write(f"- Keywords generated: {len(keywords)}")
        self.stdout.write(f"- Search queries executed: {len(search_queries)}")
        self.stdout.write(f"- Total URLs found: {len(all_urls)}")
        self.stdout.write(f"- New URLs to process: {len(new_urls)}")
        self.stdout.write(f"- New valid event URLs: {len(newly_valid_urls)}")
        self.stdout.write(f"- Total valid event URLs: {len(valid_urls)}")
        self.stdout.write(f"- Validation cache size: {len(validation_cache)}")

        # Return None instead of the list to avoid Django's management command error
        return None

    def load_validation_cache(self, cache_file: str) -> Dict[str, Dict[str, Any]]:
        """Load validation cache from file"""
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cache = json.load(f)
                return cache
            except Exception as e:
                self.stderr.write(
                    self.style.WARNING(f"Error loading validation cache: {str(e)}")
                )
        return {}

    def save_validation_cache(self, cache: Dict[str, Dict[str, Any]], cache_file: str):
        """Save validation cache to file"""
        try:
            with open(cache_file, "w") as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            self.stderr.write(
                self.style.WARNING(f"Error saving validation cache: {str(e)}")
            )

    def load_existing_valid_urls(self, output_file: str) -> List[Dict[str, Any]]:
        """Load existing valid URLs from a file"""
        if not os.path.exists(output_file):
            return []

        try:
            with open(output_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def generate_keywords(self) -> List[str]:
        """Generate the main keyword for searching open water swimming events"""
        # Just use a single keyword for more focused results
        return ["open water swimming events"]

    def get_country_languages(self, country_codes=None) -> List[Dict[str, Any]]:
        """Get country-language pairs for search"""
        COUNTRY_LANGUAGES = [
            {"country": "Switzerland", "code": "CH", "languages": ["de", "fr", "it"]},
            {"country": "Germany", "code": "DE", "languages": ["de"]},
            {"country": "France", "code": "FR", "languages": ["fr"]},
            {"country": "Italy", "code": "IT", "languages": ["it"]},
            {"country": "Spain", "code": "ES", "languages": ["es"]},
            {"country": "United Kingdom", "code": "GB", "languages": ["en"]},
            {"country": "Austria", "code": "AT", "languages": ["de"]},
            {"country": "Netherlands", "code": "NL", "languages": ["nl"]},
            {"country": "Belgium", "code": "BE", "languages": ["nl", "fr"]},
            {"country": "Portugal", "code": "PT", "languages": ["pt"]},
            {"country": "Greece", "code": "GR", "languages": ["el"]},
            {"country": "Croatia", "code": "HR", "languages": ["hr"]},
            {"country": "Sweden", "code": "SE", "languages": ["sv"]},
            {"country": "Denmark", "code": "DK", "languages": ["da"]},
            {"country": "Norway", "code": "NO", "languages": ["no"]},
            {"country": "Finland", "code": "FI", "languages": ["fi"]},
            {"country": "Ireland", "code": "IE", "languages": ["en"]},
            {"country": "Poland", "code": "PL", "languages": ["pl"]},
            {"country": "Czech Republic", "code": "CZ", "languages": ["cs"]},
            {"country": "Hungary", "code": "HU", "languages": ["hu"]},
            {"country": "Slovenia", "code": "SI", "languages": ["sl"]},
            {"country": "Malta", "code": "MT", "languages": ["mt", "en"]},
            {"country": "Cyprus", "code": "CY", "languages": ["el", "tr"]},
            {"country": "Morocco", "code": "MA", "languages": ["ar", "fr"]},
            {"country": "Tunisia", "code": "TN", "languages": ["ar", "fr"]},
            {"country": "Egypt", "code": "EG", "languages": ["ar", "en"]},
        ]

        if country_codes:
            # Filter by provided country codes
            return [c for c in COUNTRY_LANGUAGES if c["code"] in country_codes]

        return COUNTRY_LANGUAGES

    def translate_keywords(
        self, keywords: List[str], country_languages: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Translate keywords to local languages"""
        # Get unique languages
        languages = set()
        for country in country_languages:
            for lang in country["languages"]:
                languages.add(lang)

        # Remove English as it doesn't need translation
        if "en" in languages:
            languages.remove("en")

        translated_keywords = {}
        llm = OpenAI(model="gpt-4o")

        for language in languages:
            self.stdout.write(f"Translating keywords to {language}...")

            # Create a prompt for translation
            prompt = f"""
            Translate the following open water swimming related keywords to {language}:
            {json.dumps(keywords, indent=2)}
            
            Return the translations as a JSON array of strings, with no additional text or explanation.
            """

            response = llm.complete(prompt)

            try:
                # Extract JSON array from response
                import re

                # Convert the response to a string
                response_text = str(response)

                json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
                if json_match:
                    translated = json.loads(json_match.group(0))
                else:
                    # Fallback if JSON parsing fails
                    lines = [
                        line.strip()
                        for line in response_text.split("\n")
                        if line.strip()
                    ]
                    # Remove any bullet points or numbering
                    translated = [
                        re.sub(r"^[\d\-\*\•\.\s]+", "", line) for line in lines
                    ]
                    # Remove any quotes
                    translated = [keyword.strip("\"'") for keyword in translated]

                translated_keywords[language] = translated
                self.stdout.write(
                    f"  Translated {len(translated)} keywords to {language}"
                )
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Error translating to {language}: {str(e)}")
                )
                # Use original keywords as fallback
                translated_keywords[language] = keywords

        return translated_keywords

    def generate_search_queries(
        self,
        keywords: List[str],
        translated_keywords: Dict[str, List[str]],
        country_languages: List[Dict[str, Any]],
    ) -> List[str]:
        """Generate search queries combining keywords, countries, and year"""
        search_queries = []

        for country_data in country_languages:
            country = country_data["country"]

            # Add English queries for all countries
            for keyword in keywords:
                search_queries.append(f"{keyword} {country} 2025")

            # Add local language queries
            for language in country_data["languages"]:
                if language == "en":
                    continue  # Skip English as it's already covered

                if language in translated_keywords:
                    for keyword in translated_keywords[language]:
                        search_queries.append(f"{keyword} {country} 2025")

        return search_queries

    def search_for_events(self, query: str) -> List[Dict[str, Any]]:
        """Execute a Google search and extract potential event URLs"""
        try:
            # Extract country and language from the query if possible
            country_code = "ch"  # Default to Switzerland
            language = "en"  # Default to English

            # Parse the query to extract country information
            query_parts = query.split()
            for country_data in self.get_country_languages():
                if country_data["country"] in query:
                    country_code = country_data["code"]
                    # Use the first language for the country
                    language = (
                        country_data["languages"][0]
                        if country_data["languages"]
                        else "en"
                    )
                    break

            # Execute the search with appropriate country and language settings
            result = serper(query, country_code=country_code, language=language)
            data = json.loads(result)

            urls = []
            for item in data.get("organic", []):
                url = item.get("link")
                if url:
                    urls.append(
                        {
                            "url": url,
                            "title": item.get("title", ""),
                            "snippet": item.get("snippet", ""),
                            "query": query,
                            "country_code": country_code,
                            "language": language,
                        }
                    )

            return urls
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Error searching for '{query}': {str(e)}")
            )
            return []

    def validate_url_with_gpt(
        self, url_data: Dict[str, Any], scraping_service: ScrapingService
    ) -> tuple:
        """Use GPT-4o to validate if a URL is an event website and determine its type"""
        url = url_data["url"]

        try:
            # Scrape the webpage content
            content = scraping_service.scrape(url)

            if not content:
                return False, EventType.UNKNOWN, "Failed to scrape content"

            # Create a system message with instructions
            system_message = """
            You are an expert at analyzing websites related to open water swimming events.
            Your task is to determine if a webpage is related to open water swimming _events_ and classify it.
            """

            # Create a user message with the content to analyze
            user_message = f"""
            Analyze this webpage content and determine if it's related to open water swimming events in 2025 or later.
            
            Content:
            {content} 
            
            Determine:
            1. If this is a valid open water swimming event website (A race or a list of races on a specific date): True/False
            2. Whether it's for a single event or contains multiple events 
            3. Provide a brief explanation for your decision
            
            Only classify as valid if it's clearly related to open water swimming events (not pool swimming, not general sports).
            """

            # Use Pydantic model for structured output
            from pydantic import BaseModel
            from openai import OpenAI

            class EventValidation(BaseModel):
                is_valid: bool
                event_type: EventType
                explanation: str

            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

            completion = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                response_format=EventValidation,
            )

            result = completion.choices[0].message.parsed

            # Extract the validation results
            is_valid = result.is_valid
            event_type = result.event_type
            explanation = result.explanation

            return is_valid, event_type, explanation

        except Exception as e:
            return False, EventType.UNKNOWN, f"Error validating URL: {str(e)}"

    def save_urls_to_file(
        self,
        valid_urls: List[Dict[str, Any]],
        filename: str = "discovered_event_urls.json",
    ):
        """Save validated URLs to a JSON file"""
        with open(filename, "w") as f:
            json.dump(valid_urls, f, indent=2)
