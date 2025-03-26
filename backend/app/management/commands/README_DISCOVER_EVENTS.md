# Event URL Discovery Tool

This tool uses LlamaIndex's ReAct-Agent with GPT-4o to discover new open water swimming event URLs through Google Search. It follows a systematic approach to find, filter, and validate event websites.

## Prerequisites

Before using this tool, make sure you have the following environment variables set:

- `OPENAI_API_KEY`: API key for OpenAI (used for GPT-4o)
- `SERPER_API_KEY`: API key for Google Serper API (used for Google Search)
- `FIRECRAWL_API_KEY`: API key for Firecrawl (used for web scraping)

You can set these in your `.env` file in the backend directory.

## Usage

Run the command using Django's management command interface:

```bash
python manage.py discover_event_urls [options]
```

### Options

- `--limit NUMBER`: Limit the number of search queries to execute (useful for testing)
- `--output FILENAME`: Specify the output file for discovered URLs (default: `discovered_event_urls.json`)
- `--countries CODE [CODE ...]`: Limit search to specific countries by country code (e.g., `CH DE FR`)
- `--dry-run`: Run without saving to file (for testing)

### Examples

Basic usage (searches all countries):
```bash
python manage.py discover_event_urls
```

Limit to specific countries:
```bash
python manage.py discover_event_urls --countries CH DE FR
```

Test run with limited queries:
```bash
python manage.py discover_event_urls --limit 5 --dry-run
```

Custom output file:
```bash
python manage.py discover_event_urls --output new_events_2025.json
```

## How It Works

The tool follows this process:

1. **Generate Keywords**: Uses GPT-4o to generate a comprehensive list of keywords related to open water swimming events.

2. **Define Country-Language Pairs**: Works with a predefined list of European and North African countries and their languages.

3. **Translate Keywords**: Translates the keywords to each local language using GPT-4o.

4. **Generate Search Queries**: Creates search queries by combining keywords, countries, and the year "2025".

5. **Execute Google Searches**: Uses the Serper API to perform Google searches for each query.

6. **Filter Results**: Checks if discovered URLs are already in the database.

7. **Validate URLs**: Uses GPT-4o to validate if each URL is actually an open water swimming event website.

8. **Save Results**: Saves valid URLs to a JSON file for later processing.

## Output Format

The tool generates a JSON file with the following structure:

```json
[
  {
    "url": "https://example.com/event",
    "title": "Example Open Water Swim 2025",
    "snippet": "Join us for the annual open water swimming event...",
    "query": "open water swimming Switzerland 2025",
    "validation": "YES: This is a website for an open water swimming event taking place in 2025."
  },
  ...
]
```

## Processing Discovered URLs

After running this tool, you can process the discovered URLs using the included processing command:

```bash
python manage.py process_discovered_urls [options]
```

### Processing Options

- `--input FILENAME`: Specify the input JSON file (default: `discovered_event_urls.json`)
- `--limit NUMBER`: Limit the number of URLs to process
- `--dry-run`: Show commands without executing them

### Examples

Process all discovered URLs:
```bash
python manage.py process_discovered_urls
```

Process with a custom input file:
```bash
python manage.py process_discovered_urls --input new_events_2025.json
```

Test run with limited URLs:
```bash
python manage.py process_discovered_urls --limit 3 --dry-run
```

### Manual Processing

You can also manually process individual URLs using the existing event crawling system:

```bash
python manage.py crawl_events --event https://example.com/event
```

## Testing the System

A test command is included to help you verify the functionality of the event discovery system with minimal parameters:

```bash
python manage.py test_event_discovery [options]
```

### Testing Options

- `--keyword "SEARCH TERM"`: Test search with a specific keyword (default: "open water swimming Switzerland 2025")
- `--url "URL"`: Test URL validation with a specific URL (skips search if provided)

### Examples

Test the search functionality:
```bash
python manage.py test_event_discovery
```

Test with a custom search keyword:
```bash
python manage.py test_event_discovery --keyword "triathlon swim Italy 2025"
```

Test URL validation:
```bash
python manage.py test_event_discovery --url "https://example.com/event"
```

## Troubleshooting

- **API Rate Limits**: If you hit rate limits with the search or OpenAI APIs, try using the `--limit` option to reduce the number of queries.
- **Language Issues**: If translations aren't working correctly, the tool will fall back to using English keywords.
- **Validation Errors**: If URL validation is failing, check the Firecrawl API settings and ensure the websites are accessible.
- **Environment Variables**: Make sure all required environment variables are set in your `.env` file.
