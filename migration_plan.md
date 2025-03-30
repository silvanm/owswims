# Vue 2 to Vue 3 Migration Plan for OWSwims

## Overview

This document outlines the plan for migrating the OWSwims frontend application from Vue 2 to Vue 3. The migration will be performed in a phased approach to minimize disruption to the development workflow and ensure a smooth transition.

## Current Technology Stack

- **Frontend Framework**: Vue 2.x with Nuxt.js
- **State Management**: Vuex
- **API Client**: Apollo GraphQL Client
- **UI Components**: Custom Vue components with Tailwind CSS
- **Maps**: Google Maps JavaScript API
- **Date Handling**: date-fns
- **Internationalization**: nuxt-i18n
- **Form Components**: vue-slider-component, vue2-datepicker
- **Other Key Libraries**: v-tooltip, vue-easy-lightbox, vue2-touch-events

## Migration Goals

1. Upgrade from Vue 2 to Vue 3 while maintaining all existing functionality
2. Modernize the codebase to leverage Vue 3's Composition API
3. Update all dependencies to versions compatible with Vue 3
4. Improve performance and maintainability
5. Ensure backward compatibility with the existing backend API
6. Maintain the current UI/UX design

## Migration Strategy

The migration will follow a phased approach with the assistance of an AI tool like Claude to automate and guide many aspects of the migration process. This strategy is informed by the official [Vue 3 Migration Guide](https://v3-migration.vuejs.org/):

### Phase 0: Consider Migration Build (Optional)

Before beginning the full migration, we may consider using the Vue 3 Migration Build as an intermediate step:

1. **Evaluate Migration Build**
   - The Vue 3 Migration Build provides Vue 2 API compatibility with Vue 3 under the hood
   - This allows for incremental migration by running Vue 2 code on Vue 3
   - AI will help assess if this approach is suitable for our specific codebase

2. **Implement Migration Build (if chosen)**
   - Replace Vue 2 with the Vue 3 Migration Build
   - Run compatibility checks and fix immediate issues
   - Use this as a stepping stone before full migration

### Phase 1: Preparation and Analysis

1. **Create a Migration Branch**
   - Create a new branch from the main development branch for the migration work
   - This allows parallel development on the Vue 2 version if needed

2. **Dependency Analysis with AI Assistance**
   - Use AI to scan package.json and identify all Vue 2 specific dependencies
   - AI will research and recommend Vue 3 compatible alternatives
   - AI will generate a comprehensive dependency migration table
   - Human review and approval of AI recommendations

3. **Code Analysis with AI Assistance**
   - AI will scan codebase to identify Vue 2 specific patterns and APIs
   - AI will analyze components for compatibility issues
   - AI will document required changes for each component
   - Human review of AI analysis to ensure accuracy

4. **Setup Development Environment**
   - Configure a separate development environment for Vue 3 migration
   - Set up testing infrastructure
   - Prepare environment for AI-assisted development

### Phase 2: Core Infrastructure Updates

1. **Update Nuxt.js with AI Assistance**
   - AI will generate the initial Nuxt 3 configuration based on existing Nuxt 2 setup
   - AI will transform nuxt.config.js to the new format
   - Human review and testing of the generated configuration
   - **Decision made to disable SSR completely to avoid SSR-related bugs during migration**

2. **Update Build System**
   - AI will generate updated webpack configuration
   - AI will provide Vite configuration for faster development
   - AI will update ESLint and Prettier configurations
   - Human review and testing of build system changes

3. **Update State Management with AI Assistance**
   - AI will convert Vuex store to Pinia stores
   - AI will refactor store modules following best practices
   - AI will update store access patterns throughout the application
   - Human review and testing of state management changes

4. **Update Router with AI Assistance**
   - AI will migrate to Vue Router 4
   - AI will update route definitions and navigation guards
   - Human review and testing of routing functionality

### Phase 3: Component Migration with AI Assistance

1. **Shared Components**
   - AI will analyze and transform smaller, shared components first
   - AI will migrate to Vue 3 syntax
   - AI will update template syntax for v-model changes
   - AI will implement Composition API where beneficial
   - Human review and testing of each transformed component

2. **Page Components**
   - AI will migrate page components
   - AI will update lifecycle hooks
   - AI will refactor complex components using Composition API
   - Human review and testing of each transformed component

3. **Map Component**
   - Special focus on the Map.vue component as it's core to the application
   - AI-assisted migration of Google Maps integration with careful human oversight
   - Collaborative refinement of complex map functionality
   - Thorough testing for regressions

4. **Third-party Component Integration**
   - AI will identify and recommend Vue 3 compatible alternatives
   - AI will update or replace third-party components
   - Focus on DaterangeSlider, vue-tooltip, vue-easy-lightbox, etc.
   - Human review and testing of third-party integrations

### Phase 4: Feature Updates and Testing

1. **Update Apollo GraphQL Integration**
   - Migrate to Apollo Client 3.x
   - Update query components and hooks

2. **Internationalization**
   - Update i18n implementation for Vue 3
   - Test all language configurations

3. **Comprehensive Testing**
   - Unit tests for components
   - Integration tests for key workflows
   - End-to-end tests for critical user journeys
   - Performance testing

### Phase 5: Deployment and Monitoring

1. **Staging Deployment**
   - Deploy to staging environment
   - Perform UAT (User Acceptance Testing)
   - Fix any identified issues

2. **Production Deployment**
   - Deploy to production
   - Monitor for issues
   - Be prepared for rollback if necessary

3. **Post-Migration Optimization**
   - Identify opportunities for further improvements
   - Leverage Vue 3 specific features for optimization

## Breaking Changes to Address

Based on the official Vue 3 Migration Guide, we need to address these key breaking changes:

### Global API Changes
- Vue 2's global API (Vue.use, Vue.component, etc.) is now instance-based
- Global and internal APIs have been restructured to be tree-shakable

### Template Directives Changes
- `v-model` usage on components has been reworked
- `v-if` and `v-for` precedence has changed
- `v-bind="object"` now spreads properties in a different order
- `v-on:event.native` modifier has been removed

### Components Changes
- Functional components can only be created using a plain function
- Single-file component `<template>` now requires a single root node (unless using Fragments)
- Component events should now be declared with the `emits` option

### Render Function / JSX Changes
- Render function API has changed to use the h function directly
- `$scopedSlots` property has been removed, all slots exposed via `$slots`
- `$listeners` has been removed and merged into `$attrs`

### Custom Elements
- Custom elements whitelisting is now performed during template compilation
- Special `is` attribute usage has been restricted to the `<component>` tag only

### Other Notable Changes
- `destroyed` lifecycle hook renamed to `unmounted`
- `beforeDestroy` lifecycle hook renamed to `beforeUnmount`
- Props default function no longer has access to `this`
- Custom directives API has been changed to align with component lifecycle

## Detailed Migration Tasks

### Notable New Features to Leverage

The migration will allow us to take advantage of these new Vue 3 features:

1. **Composition API**
   - More flexible code organization
   - Better TypeScript integration
   - Improved reusability of logic

2. **`<script setup>` Syntax**
   - Simpler, more concise component authoring
   - Less boilerplate for Composition API usage
   - Better runtime performance

3. **Teleport**
   - Render content elsewhere in the DOM while preserving component hierarchy
   - Useful for modals, tooltips, and dropdowns

4. **Fragments**
   - Components can have multiple root nodes
   - Reduces unnecessary wrapper divs

5. **Emits Component Option**
   - Explicit declaration of emitted events
   - Better documentation and type checking

6. **SFC Style Features**
   - `v-bind` in CSS to connect component state with styles
   - Improved scoped CSS with deep selectors and slotted content targeting

7. **Suspense**
   - Handle async dependencies in the component tree
   - Provide loading states while async components resolve

### Dependencies to Update

| Current Dependency | Version | Vue 3 Compatible Alternative | Notes |
|-------------------|---------|------------------------------|-------|
| nuxt | ^2.14.6 | nuxt@3.x | Major version upgrade with significant changes |
| @nuxtjs/apollo | ^4.0.1-rc.4 | @nuxt/apollo or nuxt-apollo@next | Check for Vue 3 compatibility |
| vuex | (via nuxt) | pinia | Recommended state management for Vue 3 |
| v-tooltip | ^2.0.3 | floating-vue or @vueuse/tooltip | v-tooltip is not Vue 3 compatible |
| vue-slider-component | ^3.2.9 | Check for Vue 3 compatibility or use @vueuse/components | May need replacement |
| vue2-datepicker | ^3.9.0 | vue-datepicker-next or @vuepic/vue-datepicker | Need Vue 3 compatible version |
| vue-tour | ^1.5.0 | vue3-tour or v-tour | Check for Vue 3 compatibility |
| vue2-touch-events | ^3.1.0 | @vueuse/gesture or vue3-touch-events | Need Vue 3 compatible version |
| vue-easy-lightbox | 0.x | vue-easy-lightbox@next | Check for Vue 3 version |
| vue-star-rating | ^1.7.0 | vue3-star-rating or @vueform/rating | Need Vue 3 compatible version |
| @nuxtjs/tailwindcss | ^3.1.0 | @nuxtjs/tailwindcss@latest | Update for Nuxt 3 compatibility |
| nuxt-i18n | ^6.20.1 | @nuxtjs/i18n | Update for Nuxt 3 compatibility |

### Component Migration Priorities

1. **High Priority (Core Functionality)**
   - Map.vue (central to the application)
   - EventPane.vue
   - FilterBox.vue
   - DaterangeSlider.vue (known to be in active development)

2. **Medium Priority**
   - ReviewBox.vue
   - LoginBox.vue
   - CourseEditor.vue
   - Translatable.vue

3. **Lower Priority**
   - UI components (CloseButton.vue, Spinner.vue, etc.)
   - InfoTab.vue
   - Infotext.vue
   - Tour.vue

### Code Changes Required

1. **Global API Changes**
   - Replace Vue.use() with createApp().use()
   - Update plugin registration
   - Migrate global components to local registration

2. **Template Changes**
   - Update v-model usage (property and event names have changed)
   - Update multiple v-model bindings
   - Update filters (replace with computed properties or methods)

3. **Component Options Changes**
   - Replace mixins with composables
   - Update lifecycle hooks
   - Migrate to Composition API where beneficial

4. **Vuex to Pinia Migration**
   - Convert store modules to Pinia stores
   - Update store access patterns (mapState, mapGetters, etc.)
   - Implement store composition pattern

## Composition API Migration Strategy

For complex components, we'll adopt the Composition API to improve code organization and reusability:

1. **Extract Reusable Logic**
   - Create composables for map functionality
   - Create composables for date handling
   - Create composables for API interactions

2. **Component Refactoring**
   - Start with the script setup syntax for simpler components
   - Use explicit imports for reactive, ref, computed, etc.
   - Organize code by feature rather than by option type

3. **Example Transformation**

```javascript
// Before (Options API)
export default {
  data() {
    return {
      locations: [],
      selectedLocation: null
    }
  },
  computed: {
    filteredLocations() {
      // filtering logic
    }
  },
  methods: {
    selectLocation(location) {
      // selection logic
    }
  }
}

// After (Composition API)
import { ref, computed } from 'vue'

export default {
  setup() {
    const locations = ref([])
    const selectedLocation = ref(null)
    
    const filteredLocations = computed(() => {
      // filtering logic
    })
    
    function selectLocation(location) {
      // selection logic
    }
    
    return {
      locations,
      selectedLocation,
      filteredLocations,
      selectLocation
    }
  }
}
```

## Testing Strategy

1. **Unit Testing**
   - Test individual components after migration
   - Focus on complex components with business logic
   - Ensure all edge cases are covered

2. **Integration Testing**
   - Test component interactions
   - Focus on data flow between components
   - Test store integration

3. **End-to-End Testing**
   - Test critical user journeys
   - Ensure map functionality works correctly
   - Test filtering and search functionality

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking changes in Vue 3 | High | Thorough testing, incremental migration |
| Third-party library compatibility | High | Research alternatives, prepare fallbacks |
| Performance regression | Medium | Performance testing, optimization |
| Development delays | Medium | Phased approach, clear milestones |
| Learning curve for team | Medium | Documentation, knowledge sharing sessions |

## Migration Approach Options

Based on the official Vue 3 Migration Guide, we have several approaches to consider:

1. **Direct Migration**
   - Migrate the entire application at once
   - Best for smaller applications
   - AI assistance makes this more feasible even for larger apps

2. **Migration Build Approach**
   - Use the Vue 3 Migration Build as an intermediate step
   - Allows running Vue 2 code on Vue 3 with compatibility layer
   - Gradually update code to Vue 3 APIs
   - Good for large applications that need to maintain functionality during migration

3. **Parallel Migration**
   - Keep Vue 2 version running in production
   - Create a separate Vue 3 version in parallel
   - Gradually move features from old to new
   - Best for critical applications that cannot risk downtime

For OWSwims, we recommend the **Direct Migration with AI Assistance** approach, as the application is of moderate size and AI tools can significantly accelerate the process. However, we should keep the Migration Build as a fallback option if we encounter significant compatibility issues.

## Timeline with AI Assistance

| Phase | Estimated Duration | Key Milestones |
|-------|-------------------|---------------|
| Preparation and Analysis | 3-5 days | Dependency analysis complete, migration plan finalized |
| Core Infrastructure Updates | 1-2 weeks | Nuxt 3 setup, Pinia store implementation |
| Component Migration | 2-3 weeks | All components migrated, passing tests |
| Feature Updates and Testing | 1-2 weeks | All features working, comprehensive tests passing |
| Deployment and Monitoring | 3-5 days | Successful staging deployment, production release |

Total estimated time: 4-8 weeks

The timeline is significantly reduced due to AI assistance, which can:
- Perform initial code transformations much faster than manual rewrites
- Generate boilerplate code and configurations automatically
- Identify and fix compatibility issues systematically
- Provide immediate suggestions for Vue 3 alternatives to Vue 2 patterns

However, human oversight and testing remain critical at each stage to ensure quality and functionality.

## Post-Migration Improvements

Once the migration is complete, we can leverage Vue 3 specific features for further improvements:

1. **Performance Optimization**
   - Use Suspense for async components
   - Implement lazy loading for components
   - Optimize rendering with Fragment support

2. **Code Quality**
   - Refactor complex components using Composition API
   - Implement TypeScript for better type safety
   - Create more reusable composables

3. **Feature Enhancements**
   - Improve map performance
   - Enhance mobile experience
   - Implement new UI components

## AI-Human Collaboration Approach

To maximize the effectiveness of using an AI assistant for the migration, we'll follow these principles:

1. **Iterative Transformation**
   - AI will transform code in small, manageable chunks
   - Human review after each transformation
   - Immediate testing of transformed components
   - Feedback loop to improve AI's understanding of the codebase

2. **Knowledge Transfer**
   - AI will explain the reasoning behind transformations
   - AI will provide documentation on Vue 3 patterns being implemented
   - Human developers gain understanding of Vue 3 best practices through the process

3. **Quality Control**
   - Human developers maintain final decision-making authority
   - AI suggests multiple approaches when appropriate
   - Regular testing to ensure functionality is preserved
   - Code reviews to maintain code quality standards

4. **Division of Responsibilities**
   - AI: Initial code transformation, pattern recognition, boilerplate generation
   - Human: Architecture decisions, edge case handling, testing, final approval

## Progress Tracking

This section will be updated throughout the migration process to track progress and serve as a living document of the migration journey.

### Migration Progress Dashboard

| Phase | Status | Progress | Notes |
|-------|--------|----------|-------|
| Phase 0: Migration Build Evaluation | Completed | 100% | Decision made to use Direct Migration with AI assistance |
| Phase 1: Preparation and Analysis | Completed | 100% | Initial plan created, dependency analysis completed, test project created |
| Phase 2: Core Infrastructure Updates | Completed | 100% | Completed Nuxt 3 configuration, Pinia stores, and Apollo Client 3.x integration |
| Phase 3: Component Migration | In Progress | 85% | Successfully migrated all high and medium priority components including CloseButton, Toggle, Spinner, DaterangeSlider, FilterBox, EventPane, Map, ReviewBox, LoginBox, and Translatable. Decision made to skip CourseEditor component. |
| Phase 4: Feature Updates and Testing | In Progress | 10% | Started testing components in isolation, preparing for integration |
| Phase 5: Deployment and Monitoring | Not Started | 0% | - |

### Completed Tasks

- [x] Created initial migration plan
- [x] Reviewed official Vue 3 Migration Guide
- [x] Identified key breaking changes to address
- [x] Established AI-human collaboration approach
- [x] Created dependency analysis document (vue3-migration/dependency-analysis.md)
- [x] Completed full dependency inventory
- [x] Researched all dependencies for Vue 3 compatibility
- [x] Documented specific version recommendations
- [x] Identified high-risk dependencies
- [x] Created migration strategy for each dependency
- [x] Estimated effort for dependency updates
- [x] Evaluated Migration Build approach (decided on Direct Migration)

### Current Tasks

- [x] Set up development environment for migration
- [x] Create migration branch
- [x] Create test project for key dependencies
- [x] Create test project for migrated components
- [x] Test migrated components in isolation
- [x] Migrate FilterBox.vue component using Composition API
- [x] Integrate @vueform/slider and floating-vue in FilterBox component
- [x] Add FilterBox component to component test page
- [x] Test FilterBox component functionality (search, date range, distance slider, collapse)
- [x] Fix FilterBox component import for @vueform/slider (changed from named to default import)

### Upcoming Tasks

- [x] Begin Nuxt 3 configuration for main project
- [x] Start Vuex to Pinia migration
- [x] Configure Apollo Client 3.x for main project
- [x] Begin component migration with shared components
  - [x] Create component migration guide
  - [x] Identify shared components to migrate first
  - [x] Migrate simple UI components (CloseButton, Toggle, Spinner)
  - [x] Migrate complex components (DaterangeSlider, FilterBox, EventPane)
  - [x] Migrate Map.vue component (high priority)
    - [x] Research Vue 3 compatible approaches for Google Maps integration
    - [x] Create simplified version for testing
    - [x] Implement Composition API for map functionality
    - [x] Test map interactions and functionality
  - [x] Continue with medium priority components (ReviewBox, LoginBox)
  - [x] Continue with remaining medium priority components (Translatable)
  - [x] Update lifecycle hooks
  - [x] Implement Composition API where beneficial
  - [🔄] Test migrated components (In Progress)

- [ ] Prepare for integration phase
  - [ ] Integrate all migrated components into the main application
  - [ ] Test component interactions
  - [ ] Ensure all features work correctly
  - [ ] Prepare for deployment

- [ ] Replace mocked implementations
  - [ ] Replace Google Maps mock with actual Google Maps JavaScript API
  - [ ] Implement full i18n solution using @nuxtjs/i18n
  - [ ] Connect Pinia stores to the actual backend API
  - [ ] Implement full GraphQL queries with Apollo Client

### Integration Approach

For the integration phase, we will continue building the application in the `vue3-migration/test-project` directory rather than directly modifying the existing frontend. This approach offers several advantages:

1. **Controlled Environment**: The test project provides a clean, controlled environment where we can integrate components without disrupting the production application.

2. **Comprehensive Testing**: We can thoroughly test the entire application in isolation before considering a full replacement of the production frontend.

3. **Reduced Risk**: By keeping the Vue 3 migration separate from the production codebase, we minimize the risk of introducing bugs or regressions.

4. **Gradual Integration**: We can focus on replacing mock implementations with real API connections one by one, ensuring each integration works properly.

The integration process will follow these steps:

1. Complete the integration of all migrated components into the test project
2. Replace mock implementations with real API connections (Google Maps, i18n, GraphQL)
3. Implement any remaining features that haven't been migrated yet
4. Perform comprehensive testing in the test environment
5. Once fully tested, either:
   - Use the test project as the new production frontend (renaming directories)
   - Or copy the completed Vue 3 application to replace the existing frontend

### Component Migration Status

| Component | Status | Notes |
|-----------|--------|-------|
| CloseButton.vue | Completed | Migrated using Options API |
| Toggle.vue | Completed | Migrated using Options API |
| Spinner.vue | Completed | Migrated using Options API with vue-loading replacement |
| Map.vue | Completed | High priority, migrated with Google Maps mock plugin for testing |
| EventPane.vue | Completed | High priority, migrated with FontAwesome and vue3-touch-events integration |
| FilterBox.vue | Completed | High priority, migrated using Composition API with @vueform/slider and floating-vue integration |
| DaterangeSlider.vue | Completed | Migrated using Composition API with @vueform/slider and @vuepic/vue-datepicker |
| ReviewBox.vue | Completed | Migrated using Composition API with @chahindb7/vue-star-rating |
| LoginBox.vue | Completed | Migrated using Composition API with Pinia store integration |
| CourseEditor.vue | Skipped | Decision made to skip migration of this component |
| Translatable.vue | Completed | Migrated using Composition API with mock translation API |
| Other UI Components | Not Started | Lower priority |

### Dependency Migration Status

| Dependency | Status | Target Version | Notes |
|------------|--------|----------------|-------|
| nuxt | Completed | nuxt@3.10.x | Created initial configuration |
| @nuxtjs/apollo | Completed | nuxt-apollo@^5.0.0 | Configured Apollo Client 3.x |
| vuex | Completed | pinia | Created Pinia stores |
| v-tooltip | Completed | floating-vue@^2.0.0 | Vue 3 compatible replacement, successfully tested in FilterBox component |
| vue-slider-component | Completed | @vueform/slider@^2.1.10 | Vue 3 compatible alternative, successfully tested in FilterBox component |
| vue2-datepicker | Not Started | @vuepic/vue-datepicker@^7.4.0 | Vue 3 compatible replacement |
| vue-tour | Not Started | vue3-tour@^0.3.4 | Vue 3 compatible fork |
| vue2-touch-events | Completed | vue3-touch-events@^4.1.8 | Successfully integrated in test project |
| vue-easy-lightbox | Not Started | vue-easy-lightbox@^1.17.0 | Vue 3 compatible version |
| vue-star-rating | Not Started | vue3-star-rating@^1.1.7 | Vue 3 compatible replacement |
| @nuxtjs/tailwindcss | Not Started | @nuxtjs/tailwindcss@^6.11.2 | Update for Nuxt 3 |
| nuxt-i18n | Not Started | @nuxtjs/i18n@^8.0.0 | Update for Nuxt 3 |
| @fortawesome/fontawesome-svg-core | Completed | @fortawesome/fontawesome-svg-core@latest | Successfully integrated in test project |
| @fortawesome/vue-fontawesome | Completed | @fortawesome/vue-fontawesome@latest | Successfully integrated in test project |
| @fortawesome/free-solid-svg-icons | Completed | @fortawesome/free-solid-svg-icons@latest | Successfully integrated in test project |

### Issues and Blockers

| Issue | Impact | Resolution Plan | Status |
|-------|--------|----------------|--------|
| Google Maps integration with Vue 3 | Medium | Research Vue 3 compatible approaches, test in isolation | Pending |
| Complex component refactoring | Medium | Use Composition API, break down into smaller components | Pending |
| Apollo Client 3.x migration | Medium | Follow Apollo migration guide, test queries in isolation | Resolved |

## Development Guidelines for AI Agents

When working on this migration, AI agents should follow these guidelines:

### File and Project Structure

- **Reuse existing files and projects**: Always modify existing files rather than creating new ones. The project structure has been carefully designed and should be maintained.
  - Use the existing test project at `vue3-migration/test-project` for testing migrated components
  - Update existing components in `frontend/` directory when migrating
  - Use the existing Vue 3 test environment in `frontend/vue3-test/` for additional testing if needed

### Component Migration Approach

- **SSR Compatibility**: Many components need to work in both browser and server-side rendering environments
  - Wrap components with `<client-only>` tags to prevent SSR issues
  - Move window-dependent code to onMounted lifecycle hooks
  - Check for window existence before using it

- **Dependency Handling**:
  - Use simplified implementations that don't rely on external dependencies for testing
  - Replace Vue 2 specific dependencies with Vue 3 compatible alternatives
  - Test components in isolation before integrating them into the main application

### Documentation Updates

- **Keep documentation current**: Always update this plan and the migration tracker when making progress
  - Document any issues encountered and their solutions
  - Keep the component migration status table up to date
  - Add notes about specific challenges or solutions for each component

## Conclusion

This migration plan provides a structured approach to upgrading the OWSwims frontend from Vue 2 to Vue 3 with the assistance of AI tools like Claude. By leveraging AI for code transformation while maintaining human oversight, we can significantly accelerate the migration process while ensuring quality.

The AI-assisted approach reduces the manual effort required for repetitive transformation tasks, allowing the development team to focus on architecture decisions, edge cases, and ensuring the application functions correctly. This collaborative approach combines the speed and pattern recognition capabilities of AI with the contextual understanding and quality control of human developers.

The migration will still require careful planning and testing, but with AI assistance, we can complete the process more efficiently while still realizing the benefits of Vue 3's improved performance, better TypeScript support, and the Composition API.

This document will be continuously updated throughout the migration process to track progress, document decisions, and serve as a reference for the team.
