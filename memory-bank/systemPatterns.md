# System Patterns

## Architecture Overview

OWSwims follows a client-server architecture with a clear separation between the frontend and backend:

```mermaid
flowchart TD
    Client[Vue.js/Nuxt.js Frontend]
    Server[Django Backend]
    DB[(PostgreSQL Database)]
    GMap[Google Maps API]
    
    Client <--> |GraphQL| Server
    Server <--> DB
    Client <--> GMap
```

## Backend Architecture

The backend follows a Django-based architecture with GraphQL for API communication:

```mermaid
flowchart TD
    Models[Django Models]
    GraphQL[GraphQL Schema]
    Auth[Authentication]
    Services[Services]
    
    Models --> GraphQL
    Auth --> GraphQL
    Services --> Models
    GraphQL --> Services
```

### Key Components

1. **Models**: Django ORM models representing the data structure
   - Location
   - Event
   - Race
   - Organizer
   - Review

2. **GraphQL API**: Provides a flexible query interface for the frontend
   - Queries: Data retrieval operations
   - Mutations: Data modification operations
   - Filters: Complex filtering capabilities

3. **Services**: Business logic encapsulation
   - Event verification
   - Location management and verification
   - Rating calculations
   - Event crawling and processing
   - Automated location processing

## Frontend Architecture

The frontend follows a Nuxt.js architecture with Vue components:

```mermaid
flowchart TD
    Pages[Nuxt Pages]
    Components[Vue Components]
    Store[Vuex Store]
    Apollo[Apollo GraphQL Client]
    
    Pages --> Components
    Components --> Store
    Store --> Apollo
    Apollo --> Backend[Backend API]
```

### Key Components

1. **Map Component**: Core interactive map using Google Maps
   - Location markers
   - Clustering
   - Race track visualization

2. **Filter Components**: User interface for filtering events
   - DaterangeSlider
   - Distance filters
   - Keyword search

3. **Event Display**: Components for showing event details
   - EventPane
   - Reviews
   - Race information

4. **State Management**: Vuex store for application state
   - User preferences
   - Selected locations
   - Filter settings

## Design Patterns

1. **Repository Pattern**: Used in the Django models to encapsulate data access logic

2. **Component-Based Architecture**: Frontend is built with reusable Vue components

3. **Flux Pattern**: Implemented via Vuex for unidirectional data flow

4. **Observer Pattern**: Used for reactive updates in the Vue.js components

5. **Factory Pattern**: Used for creating complex objects like map markers

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Frontend UI
    participant Store as Vuex Store
    participant API as GraphQL API
    participant DB as Database
    
    User->>UI: Interact with map/filters
    UI->>Store: Update state
    Store->>API: Request data
    API->>DB: Query database
    DB->>API: Return results
    API->>Store: Update state with results
    Store->>UI: Reactive update
    UI->>User: Display updated view
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant UI as Frontend UI
    participant Auth as Auth Service
    participant API as GraphQL API
    participant DB as Database
    
    User->>UI: Login credentials
    UI->>Auth: Authentication request
    Auth->>DB: Validate credentials
    DB->>Auth: Validation result
    Auth->>UI: JWT token
    UI->>API: Authenticated requests with JWT
    API->>UI: Protected data
```

## Key Technical Decisions

1. **GraphQL over REST**: Provides more flexible querying capabilities and reduces over-fetching

2. **Django + PostgreSQL**: Robust ORM and relational database for complex data relationships

3. **Vue.js + Nuxt.js**: Component-based frontend with server-side rendering capabilities

4. **Google Maps Integration**: Industry-standard mapping solution with extensive features

5. **JWT Authentication**: Stateless authentication for scalability

6. **LLM-based Crawling System**: Agent-based approach for automated event data extraction

7. **Django Q for Asynchronous Processing**: Task queue for handling time-consuming operations in the background

## Event Crawling System

The event crawling system uses LLM-based agents to automate the extraction of swimming event data from websites:

```mermaid
flowchart TD
    Command[Django Management Command]
    Crawler[EventCrawler]
    Processor[EventProcessor]
    Scraper[ScrapingService]
    LLM[OpenAI GPT-4o]
    Firecrawl[Firecrawl API]
    Profiles[Crawl Profiles]
    DB[(Database)]
    
    Command --> Crawler
    Command --> Processor
    Crawler --> Scraper
    Processor --> Scraper
    Scraper --> Firecrawl
    Profiles --> Scraper
    Profiles --> Crawler
    Crawler --> LLM
    Processor --> LLM
    Processor --> DB
```

### Key Components

1. **Django Management Command**: Entry point for the crawling system
   - `crawl_events.py`: Main command for crawling and processing events
   - Supports single event processing, multi-event crawling, and profile-based crawling
   - `list_crawl_profiles.py`: Command to list available crawl profiles

2. **Event Crawler**: Finds event URLs from swimming event websites
   - Uses LLM agent to identify and extract event URLs
   - Groups related URLs for the same event
   - Supports crawl profiles for website-specific interactions

3. **Event Processor**: Extracts structured data from event pages
   - Uses LLM agent to parse and extract event details
   - Maps extracted data to database models

4. **Scraping Service**: Handles web page content extraction
   - Uses Firecrawl API for reliable web scraping
   - Optimized for event page content
   - Supports actions from crawl profiles for interactive scraping

5. **Crawl Profiles**: Configuration files for website-specific interactions
   - JSON files with website-specific actions
   - Supports various action types (wait, click, scroll, etc.)
   - Enables scraping of sites requiring user interaction

### Data Flow

```mermaid
sequenceDiagram
    participant Admin
    participant Command as Django Command
    participant Crawler as EventCrawler
    participant Processor as EventProcessor
    participant LLM as GPT-4o
    participant Scraper as ScrapingService
    participant DB as Database
    
    Admin->>Command: Run crawl_events command
    Command->>Crawler: Get event URLs
    Crawler->>Scraper: Scrape website
    Scraper-->>Crawler: HTML content
    Crawler->>LLM: Extract event URLs
    LLM-->>Crawler: List of URL sets
    Crawler-->>Command: URL sets for events
    
    loop For each event
        Command->>Processor: Process event URLs
        Processor->>Scraper: Scrape event pages
        Scraper-->>Processor: HTML content
        Processor->>LLM: Extract structured data
        LLM-->>Processor: Event JSON data
        Processor->>DB: Create/update records
        DB-->>Processor: Confirmation
        Processor-->>Command: Processing result
    end
```

## Asynchronous Processing System

The asynchronous processing system uses Django Q to handle time-consuming operations in the background:

```mermaid
flowchart TD
    Admin[Admin Interface]
    Tasks[Django Q Tasks]
    Cluster[Django Q Cluster]
    Hooks[Task Hooks]
    DB[(PostgreSQL Database)]
    
    Admin --> Tasks
    Tasks --> Cluster
    Cluster --> DB
    Cluster --> Hooks
    Hooks --> DB
```

### Key Components

1. **Django Q Cluster**: Background worker process that executes tasks
   - Configured in `settings.py` with parameters for workers, timeouts, etc.
   - Runs as a separate process from the Django server
   - Can be started via VS Code launch configuration or command line

2. **Asynchronous Tasks**: Functions that run in the background
   - `crawl_single_event_async`: Crawls a single event asynchronously
   - `verify_locations_async`: Verifies locations asynchronously
   - `process_event_urls_async`: Processes event URLs asynchronously

3. **Task Hooks**: Functions that run after task completion
   - Log task completion status
   - Create admin log entries for successful tasks
   - Log errors for failed tasks

4. **Admin Interface Integration**: Custom actions in the admin interface
   - "Crawl Single Event" action for events
   - "Process selected unverified locations" action for locations

### Benefits

- Improved user experience by keeping the admin interface responsive
- Better resource utilization through distributed task processing
- Reliability with automatic retry for failed tasks
- Scalability by adjusting the number of workers

### Deployment

The Django Q cluster is deployed as a separate container in Kubernetes:

```mermaid
flowchart TD
    Main[Main Django Container]
    QCluster[Django Q Cluster Container]
    DB[(PostgreSQL Database)]
    
    Main --> DB
    QCluster --> DB
```

- Both containers use the same Docker image
- The Django Q container runs the `python manage.py qcluster` command
- Both containers share the same environment variables and secrets
- The Django Q container can be enabled/disabled via configuration
- Resource limits can be configured separately for the Django Q container

### Data Flow

```mermaid
sequenceDiagram
    participant Admin
    participant AdminUI as Admin Interface
    participant Task as Async Task
    participant Cluster as Django Q Cluster
    participant Hook as Task Hook
    participant DB as Database
    
    Admin->>AdminUI: Trigger async action
    AdminUI->>Task: Submit task to Django Q
    Task-->>AdminUI: Return task ID
    AdminUI-->>Admin: Show confirmation message
    
    Cluster->>Task: Execute task in background
    Task->>DB: Perform database operations
    DB-->>Task: Return results
    Task-->>Cluster: Complete task
    
    Cluster->>Hook: Call task hook
    Hook->>DB: Log task completion
    Hook-->>Cluster: Hook completed
```

## Location Verification System

The location verification system automates the process of verifying and enhancing location data:

```mermaid
flowchart TD
    Command[process_unverified_locations Command]
    Admin[Admin Interface Action]
    Processor[Location Processor]
    GoogleMaps[Google Maps API]
    GooglePlaces[Google Places API]
    GCS[Google Cloud Storage]
    DB[(Database)]
    
    Command --> Processor
    Admin --> Processor
    Processor --> GoogleMaps
    Processor --> GooglePlaces
    GooglePlaces --> GCS
    Processor --> DB
```

### Key Components

1. **Django Management Command**: Entry point for batch processing
   - `process_unverified_locations.py`: Command for processing unverified locations
   - Supports limiting the number of locations to process
   - Option for automatic verification after processing
   - Dry run mode for testing

2. **Admin Interface Integration**: Allows processing from the admin UI
   - Custom admin action for processing selected locations
   - Filtering for unverified locations
   - Detailed feedback on processing results

3. **Location Processor**: Core processing logic
   - Geocoding using the full address field
   - Place search using Google Places API
   - Header image selection from place photos
   - Coordinate refinement from identified places

4. **Multi-Strategy Approach**: Fallback mechanisms for reliability
   - Primary: Find place from address (matching frontend behavior)
   - Secondary: Text search with address
   - Tertiary: Nearby search with water type-specific place types

### Data Flow

```mermaid
sequenceDiagram
    participant Admin
    participant Command as Django Command
    participant Processor as Location Processor
    participant GMaps as Google Maps API
    participant GPlaces as Google Places API
    participant GCS as Google Cloud Storage
    participant DB as Database
    
    Admin->>Command: Run process_unverified_locations
    Command->>DB: Get unverified locations
    DB-->>Command: Unverified location data
    
    loop For each location
        Command->>Processor: Process location
        
        alt No coordinates
            Processor->>GMaps: Geocode address
            GMaps-->>Processor: Coordinates
            Processor->>DB: Update coordinates
        end
        
        alt No header image
            Processor->>GPlaces: Find place from address
            GPlaces-->>Processor: Place details & photos
            Processor->>GPlaces: Get photo
            GPlaces-->>Processor: Photo data
            Processor->>GCS: Store image
            GCS-->>Processor: Image URL
            Processor->>DB: Update header_photo
        end
        
        Processor-->>Command: Processing result
    end
    
    Command->>Admin: Summary report
```
