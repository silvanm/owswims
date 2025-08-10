# OWSwims

Open Water Swims (OWSwims) is a web application designed to help open water swimming enthusiasts discover, track, and review swimming events around the world.

## Development Environment

Edit this application always in VS Code. Not in PyCharm anymore.

## Getting Started

### Environment Setup

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your API keys in `.env`:**
   - **Google Maps API Key**: Get from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - **Google Cloud Credentials**: Download service account JSON file from GCP Console
   - **Django Secret Key**: Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
   - Set database password and other configuration

3. **⚠️ Important**: Never commit the `.env` file or credential files to version control!

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Start the development server:
   ```
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

## Importing Events

OWSwims uses an LLM-based agent system to automatically import swimming events from websites. There are two main ways to import events:

### 1. Process a Single Event

To process a single event from one or more URLs (e.g., event page and registration page):

```bash
cd backend
python manage.py crawl_events --event https://example.com/event1 https://example.com/event2
```

This command will:
- Scrape the provided URLs
- Use an LLM agent to extract structured data about the event
- Create or update the event in the database with all relevant information

### 2. Crawl Multiple Events

To crawl and process multiple events from a website that lists many events:

```bash
cd backend
python manage.py crawl_events --crawl https://example.com/events
```

This command will:
- Scrape the provided URL
- Use an LLM agent to identify all individual event URLs
- Process each event URL to extract structured data
- Create or update multiple events in the database

### Optional Parameters

- `--limit <number>`: Limit the number of events to process (useful for testing)
  ```bash
  python manage.py crawl_events --crawl https://example.com/events --limit 5
  ```

### Requirements

The event import system requires the following environment variables to be set:
- `FIRECRAWL_API_KEY`: API key for the Firecrawl web scraping service
- `OPENAI_API_KEY`: API key for OpenAI (used by the LLM agent)

These can be set in the `backend/.env` file.
