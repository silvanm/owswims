# Active Context

## Current Focus
The current development focus is on improving code organization, reducing duplication, and enhancing maintainability through shared services. We've recently completed a significant refactoring of the geocoding functionality into a shared service.

The location verification system continues to be an important focus area, now enhanced with a centralized geocoding service that provides consistent functionality across different parts of the application.

The latest improvements include:
1. Creation of a shared `GeocodingService` class that consolidates all geocoding functionality
2. Refactoring of existing commands and services to use the shared geocoding service
3. Removal of duplicated geocoding logic across multiple files
4. Removal of unused Scrapy functionality and dependencies
5. Enhanced maintainability through centralized geocoding logic

These enhancements significantly improve code organization and maintainability while ensuring consistent geocoding behavior throughout the application.

The event crawling system with crawl profiles feature also remains an important focus area. This allows for defining reusable profiles with Firecrawl actions for different event websites, making it easier to interact with pages that require specific actions (like accepting cookies or clicking "load more" buttons) before scraping. The crawling system now also supports asynchronous processing through Django Q.

## Recent Changes

### Fixed LocationCountry Enum Error
- Fixed GraphQL error "Expected a value of type 'LocationCountry' but received: UK"
- Updated EventProcessor to properly handle country codes
  - Added "UK" mapping to "GB" in country_name_mappings dictionary
  - Improved the flow to ensure geocoded country codes from Google Maps API are used
  - Added better logging for country code conversions
  - Fixed bug with incorrect variable reference in error message
- Updated existing database records with "UK" country code to use "GB" instead
- These changes ensure all country codes stored in the database are consistent with ISO 3166-1 standards (GB for United Kingdom)
- Prevents GraphQL schema validation errors when retrieving locations

### Location Verification
- Added `verified_at` timestamp field to the Location model
- This field is set when an administrator verifies the location information
- Similar to the existing event verification system
- Helps ensure location data accuracy
- Added `verified_at` column to the location admin list view
- Implemented filtering by verification status in the admin interface
- Added bulk actions to verify/unverify multiple locations at once
- Added `is_verified()` helper method to the Location model
- Implemented automated location processing
  - Created `process_unverified_locations` management command
  - Added admin action for batch processing from the UI
  - Improved geocoding to use full address for better accuracy
  - Integrated with Google Places API for place search
  - Implemented automatic header image selection
  - Added coordinate refinement from identified places
  - Added robust error handling and detailed logging

### Frontend Components
- The DaterangeSlider component is currently being worked on
- It provides date range filtering for events using both a slider and calendar view
- Uses vue2-datepicker for the calendar interface
- Supports internationalization for date formats

### Environment Configuration
- Backend environment variables are being managed in the .env file
- Contains database connection details, API keys, and service configurations
- Includes keys for:
  - Google Maps API
  - SparkPost email service
  - Sentry error tracking
  - Firebase/Google Cloud

## Current Challenges

### Data Quality
- Ensuring accuracy of location data
- Implementing verification workflows for both events and locations
- Maintaining data consistency across the platform

### User Experience
- Optimizing the map interface for both desktop and mobile users
- Improving filter interactions for better event discovery
- Enhancing race track visualization

## Next Steps

### Short-term Tasks
1. Complete the location verification system implementation
2. Update admin interface to support location verification
3. Enhance the DaterangeSlider component for better usability
4. Add visual indicators for verified locations on the map

### Primary Development Goal
1. Automated Event Import Tool
   - Develop a tool for automatically importing swims from third-party websites
   - Implementation of an LLM-based agent system for crawling and processing event data
   - Uses Firecrawl for web scraping and OpenAI's GPT-4o for data extraction
   - Structured as a Django management command with supporting services
   - Capable of both processing individual events and crawling multiple events from a website
   - Filters for future events only, using dynamically generated current date
   - Replacing the experimental Agentic crawler approach
   - Reduce manual data entry and increase event coverage

2. Event Fuzzy Search Service
   - Develop a service for quickly finding events by name and date using fuzzy search
   - Use case: Processing calendars like https://anatreselvagge.wordpress.com/2025/02/09/traversate2025/
   - Avoid having to scrape each event when many are already in the system
   - Implement efficient matching algorithm to identify existing events
   - Support partial name matches and approximate date matching
   - Integrate with the event crawler to check for existing events before processing

### Long-term Vision
1. Develop a mobile app for on-the-go event discovery
2. Implement user profiles with event history and preferences
3. Add event registration integration
4. Expand to more regions with localized content

## Active Decisions

### Technical Decisions
- Using GraphQL for flexible querying capabilities
- Leveraging Google Maps for geospatial visualization
- Implementing a component-based frontend architecture
- Using Kubernetes for scalable deployment

### Product Decisions
- Focus on data quality through verification systems
- Prioritize map-based discovery experience
- Support multiple languages for international accessibility
- Balance features for both swimmers and event organizers
