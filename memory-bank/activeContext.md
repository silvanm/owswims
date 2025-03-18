# Active Context

## Current Focus
The current development focus is on enhancing the event crawling system with the implementation of a crawl profiles feature. This allows for defining reusable profiles with Firecrawl actions for different event websites, making it easier to interact with pages that require specific actions (like accepting cookies or clicking "load more" buttons) before scraping.

The location verification system also continues to be a focus area. A recent migration (0042_add_verified_at_to_location.py) added a `verified_at` timestamp field to the Location model, similar to the existing verification field for events. This allows administrators to mark locations as verified, improving data quality and user trust.

## Recent Changes

### Location Verification
- Added `verified_at` timestamp field to the Location model
- This field is set when an administrator verifies the location information
- Similar to the existing event verification system
- Helps ensure location data accuracy
- Added `verified_at` column to the location admin list view
- Implemented filtering by verification status in the admin interface
- Added bulk actions to verify/unverify multiple locations at once
- Added `is_verified()` helper method to the Location model

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
