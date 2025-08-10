# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Use the files in /memory-bank to learn about this project.

## Development Commands

### Backend (Django)
```bash
cd backend
python manage.py runserver          # Run development server
python manage.py migrate            # Apply database migrations
python manage.py makemigrations     # Create new migrations
python manage.py test               # Run tests
pytest                              # Run tests with pytest
python manage.py check              # Django system check
flake8 backend/                     # Lint Python code (from project root)
```

### Frontend (Nuxt.js)
```bash
cd frontend
npm run dev                         # Run development server
npm run build                       # Build for production
npm run lint                        # Lint JavaScript/Vue files
```

### Event Management Commands
```bash
cd backend
python manage.py crawl_events --event <url>                    # Process single event
python manage.py crawl_events --crawl <url> --limit <n>        # Crawl multiple events
python manage.py list_crawl_profiles                           # List available crawl profiles
python manage.py process_unverified_locations                  # Process location data
python manage.py geocode                                       # Geocode locations
```

## Architecture Overview

### Backend Architecture
The Django backend follows a service-oriented pattern:

- **Models**: Core data models (Event, Location, Organizer, Race, Review, ApiToken) in `app/models.py`
- **Services**: Business logic separated into service classes in `app/services/`
  - `EventCrawler`: LLM-based event import system using Firecrawl and OpenAI
  - `EventProcessor`: Processes scraped event data into structured format
  - `GeocodingService`: Centralized location geocoding with Google Maps API
  - `LLMService`: OpenAI integration for event data extraction
- **GraphQL API**: Complete GraphQL schema in `app/graphql/` with queries, mutations, and node definitions
- **Management Commands**: Django commands for batch operations in `app/management/commands/`
- **Task Processing**: Django Q for asynchronous tasks

### Frontend Architecture
Nuxt.js SPA with Vue 2:

- **Components**: Reusable Vue components in `components/` (Map.vue, EventPane.vue, FilterBox.vue, etc.)
- **Pages**: Auto-routed pages in `pages/`
- **Store**: Vuex store modules in `store/` for state management
- **Layouts**: Page layouts in `layouts/`
- **Internationalization**: Multi-language support via nuxt-i18n with locale files

### Key Integration Points

#### LLM-Based Event Import System
The core innovation is the automated event import system:
- **Input**: Website URLs containing event information
- **Process**: Firecrawl scraping → OpenAI processing → structured data extraction
- **Output**: Event, Race, Location, and Organizer records in database
- **Profiles**: JSON configuration files in `app/crawl_profiles/` for site-specific scraping

#### Data Flow
1. **Frontend**: Vue components → Apollo GraphQL client → Backend GraphQL API
2. **Backend**: GraphQL resolvers → Django ORM → PostgreSQL
3. **Import**: Management commands → Services → Models → Database
4. **Processing**: Django Q tasks for async operations

### Environment Requirements
- `FIRECRAWL_API_KEY`: Required for web scraping
- `OPENAI_API_KEY`: Required for LLM-based event processing
- Standard Django environment variables for database, media storage, etc.

## Development Notes

- **Preferred Editor**: VS Code (not PyCharm)
- **Python Style**: Line length 88 chars, flake8 linting with E203 ignore
- **JavaScript Style**: Prettier with single quotes, no semicolons
- **Testing**: pytest for backend, configured in `pytest.ini`
- **Database**: PostgreSQL with standard Django migrations
- **Deployment**: Docker + Kubernetes with Helm charts in `helm/`