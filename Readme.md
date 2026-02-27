# OWSwims

Open Water Swims (OWSwims) is a web application designed to help open water swimming enthusiasts discover, track, and review swimming events around the world.

## Development Environment

Edit this application always in VS Code. Not in PyCharm anymore!

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
   uv sync
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

## Management Commands

OWSwims includes a comprehensive set of Django management commands for event import, data maintenance, and administration.

For detailed documentation of all available commands, see:
**[backend/app/management/commands/README.md](backend/app/management/commands/README.md)**

### Quick Examples

```bash
cd backend

# Import a single event
python manage.py crawl_events --event https://example.com/event

# Crawl multiple events from a website
python manage.py crawl_events --crawl https://example.com/events --limit 5

# Discover new event URLs via Google Search
python manage.py discover_event_urls --countries CH DE FR

# Update next year's events automatically
python manage.py update_next_year_events 2026

# Geocode locations
python manage.py geocode
```

### Required Environment Variables

Set these in `backend/.env`:
- `FIRECRAWL_API_KEY`: Web scraping service
- `OPENAI_API_KEY`: LLM processing
- `SERPER_API_KEY`: Google Search (for `discover_event_urls`)
- `GOOGLE_MAPS_API_KEY`: Geocoding and place images
