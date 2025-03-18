# Crawl Profiles

This directory contains crawl profiles for different event websites. Each profile defines a set of actions to perform before scraping a website, such as clicking buttons, accepting cookies, or loading more content.

## Profile Format

Profiles are stored as JSON files with the following structure:

```json
{
  "name": "Profile Name",
  "start_url": "https://example.com/events/",
  "actions": [
    {"type": "wait", "milliseconds": 2000},
    {"type": "click", "selector": "button.accept-cookies"},
    {"type": "wait", "milliseconds": 1000},
    {"type": "click", "selector": "button.load-more-events"},
    {"type": "wait", "milliseconds": 3000},
    {"type": "scrape"}
  ],
  "description": "Description of what this profile does"
}
```

### Action Types

The following action types are supported:

- `wait`: Wait for a specified number of milliseconds
- `click`: Click on an element matching the specified CSS selector
- `write`: Type text into a focused element
- `press`: Press a keyboard key
- `scroll_down`: Scroll down the page
- `scroll_up`: Scroll up the page
- `scrape`: Capture the page content at this point

## Usage

To use a profile with the crawl_events command:

```bash
python manage.py crawl_events --profile outdoorswimmer
```

To list all available profiles:

```bash
python manage.py list_crawl_profiles
```

## Adding New Profiles

To add a new profile:

1. Create a new JSON file in this directory with the profile ID as the filename (e.g., `example.json`)
2. Define the profile structure as shown above
3. Test the profile with `--dry-run` to ensure it works correctly:
   ```bash
   python manage.py crawl_events --profile example --dry-run
   ```

## Debugging Profiles

If a profile isn't working as expected:

1. Check the CSS selectors using browser developer tools
2. Adjust wait times to ensure the page has time to load
3. Make sure the final action is `scrape` to capture the page content
