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
   - Location management
   - Rating calculations

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
