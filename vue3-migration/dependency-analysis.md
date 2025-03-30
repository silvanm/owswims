# Vue 2 to Vue 3 Dependency Analysis

This document tracks the analysis of dependencies in the OWSwims frontend project for migration from Vue 2 to Vue 3.

## Overview

The dependency analysis is a critical part of Phase 1 in our Vue 3 migration plan. This document will:
1. List all current dependencies from package.json
2. Analyze Vue 2 specific dependencies
3. Research and recommend Vue 3 compatible alternatives
4. Document any breaking changes or migration considerations

## Current Dependencies

After examining the package.json file, here is the complete list of dependencies that need to be analyzed for Vue 3 compatibility:

### Production Dependencies

| Current Dependency | Version | Vue 3 Compatible? | Recommended Alternative | Notes |
|-------------------|---------|-------------------|-------------------------|-------|
| nuxt | ^2.14.6 | No | nuxt@3.x | Major version upgrade with significant changes. Latest version is 3.10.x |
| @nuxtjs/apollo | ^4.0.1-rc.4 | No | @nuxt/apollo@^5.0.0 | The official Apollo module for Nuxt 3 |
| @nuxtjs/toast | ^3.3.1 | No | @nuxtjs/toast@^2.0.0 or @morev/vue-transitions | Current version not compatible with Nuxt 3, alternatives available |
| @fortawesome/free-regular-svg-icons | ^5.15.3 | Yes | Same (or upgrade to ^6.5.1) | Font Awesome icons are framework-agnostic |
| @googlemaps/markerclustererplus | ^1.0.3 | Yes | @googlemaps/markerclusterer@^2.5.3 | Framework-agnostic library, but newer version available |
| @sentry/tracing | ^6.2.3 | Yes | @sentry/vue@7.x | Need to update to latest version for Vue 3 |
| @sentry/vue | ^6.2.3 | No | @sentry/vue@^7.101.1 | Need Vue 3 compatible version |
| apollo-cache-inmemory | ^1.6.6 | No | @apollo/client@^3.8.10 | Apollo Client 3.x is required for Vue 3 |
| axios | ^0.21.1 | Yes | axios@^1.6.7 | Framework-agnostic HTTP client, but should update to latest version |
| core-js | ^3.6.5 | Yes | core-js@^3.36.0 | JavaScript polyfills, framework-agnostic |
| date-fns | ^2.16.1 | Yes | date-fns@^3.3.1 | Framework-agnostic date utility library |
| dayjs | ^1.10.4 | Yes | dayjs@^1.11.10 | Framework-agnostic date utility library |
| google-distance-matrix | ^1.1.1 | Yes | Same | Framework-agnostic Google API wrapper |
| google-maps | ^4.3.3 | Yes | Same | Framework-agnostic Google Maps loader |
| graphql | ^15.3.0 | Yes | graphql@^16.8.1 | Framework-agnostic GraphQL library |
| graphql-tag | ^2.11.0 | Yes | graphql-tag@^2.12.6 | Framework-agnostic GraphQL utility |
| lodash | ^4.17.20 | Yes | lodash@^4.17.21 | Framework-agnostic utility library |
| logrocket | ^1.0.14 | Yes | logrocket@^4.0.4 | Needs configuration updates for Vue 3 |
| nuxt-i18n | ^6.20.1 | No | @nuxtjs/i18n@^8.0.0 | Need to update for Nuxt 3 compatibility |
| sass | ^1.30.0 | Yes | sass@^1.71.1 | Framework-agnostic CSS preprocessor |
| sass-loader | ^10.1.0 | Yes | sass-loader@^13.3.2 | Need version update for Webpack 5 in Nuxt 3 |
| v-tooltip | ^2.0.3 | No | floating-vue@^2.0.0 | v-tooltip is not Vue 3 compatible, floating-vue is its Vue 3 version |
| vue-country-flag | ^2.1.1 | No | vue-country-flag-next@^2.3.2 | Vue 3 compatible fork available |
| vue-easy-lightbox | 0.x | No | vue-easy-lightbox@^1.17.0 | Vue 3 compatible version available |
| vue-loading-template | ^1.3.2 | No | vue-loading@^3.0.1 or @vueuse/core | Not compatible with Vue 3, alternatives available |
| vue-slider-component | ^3.2.9 | No | @vueform/slider@^2.1.10 | Vue 3 compatible alternative with similar features |
| vue-star-rating | ^1.7.0 | No | vue3-star-rating@^1.1.7 or @vueform/rating | Vue 3 compatible alternatives available |
| vue-tour | ^1.5.0 | No | vue3-tour@^0.3.4 | Vue 3 compatible fork available |
| vue2-datepicker | ^3.9.0 | No | vue-datepicker-next@^1.0.3 or @vuepic/vue-datepicker@^7.4.0 | Vue 3 compatible alternatives available |
| vue2-touch-events | ^3.1.0 | No | @vueuse/gesture@^2.0.0 or vue3-touch-events@^4.1.8 | Vue 3 compatible alternatives available |

### Development Dependencies

| Current Dependency | Version | Vue 3 Compatible? | Recommended Alternative | Notes |
|-------------------|---------|-------------------|-------------------------|-------|
| @fortawesome/free-brands-svg-icons | ^5.15.1 | Yes | Same (or upgrade to ^6.5.1) | Framework-agnostic icons |
| @fortawesome/free-solid-svg-icons | ^5.15.1 | Yes | Same (or upgrade to ^6.5.1) | Framework-agnostic icons |
| @intlify/vue-i18n-loader | ^2.0.0-rc.1 | No | @intlify/unplugin-vue-i18n@^1.5.0 | Vue 3 compatible version required |
| @nuxtjs/eslint-config | ^3.1.0 | No | @nuxtjs/eslint-config@^12.0.0 | Updated version for Vue 3/Nuxt 3 |
| @nuxtjs/eslint-module | ^2.0.0 | No | @nuxtjs/eslint-module@^4.1.0 | Updated version for Nuxt 3 |
| @nuxtjs/fontawesome | ^1.1.2 | No | @nuxtjs/fontawesome@^2.0.0 | Need to check for Nuxt 3 compatibility |
| @nuxtjs/google-fonts | ^1.1.3 | No | @nuxtjs/google-fonts@^3.1.1 | Updated version for Nuxt 3 |
| @nuxtjs/google-gtag | ^1.0.4 | No | @nuxtjs/google-gtag@^2.1.0 | Updated version for Nuxt 3 |
| @nuxtjs/tailwindcss | ^3.1.0 | No | @nuxtjs/tailwindcss@^6.11.2 | Updated version for Nuxt 3 |
| @tailwindcss/custom-forms | ^0.2.1 | No | @tailwindcss/forms@^0.5.7 | Renamed in newer versions |
| babel-eslint | ^10.1.0 | No | @babel/eslint-parser@^7.23.10 | babel-eslint is deprecated |
| cypress | ^6.8.0 | Yes | cypress@^13.6.4 | Framework-agnostic E2E testing, but newer version available |
| eslint | ^7.10.0 | Yes | eslint@^8.57.0 | Need configuration updates for Vue 3 |
| eslint-config-prettier | ^6.12.0 | Yes | eslint-config-prettier@^9.1.0 | Need version update for ESLint 8 |
| eslint-plugin-nuxt | ^1.0.0 | No | eslint-plugin-nuxt@^4.0.0 | Updated version for Nuxt 3 |
| eslint-plugin-prettier | ^3.1.4 | Yes | eslint-plugin-prettier@^5.1.3 | Need version update for ESLint 8 |
| prettier | ^2.1.2 | Yes | prettier@^3.2.5 | Framework-agnostic code formatter, but newer version available |

## Dependency Migration Analysis

### High Priority Dependencies

These dependencies are critical to the application and require careful migration planning:

1. **Nuxt 2 to Nuxt 3**
   - **Complexity**: High
   - **Impact**: High
   - **Migration Path**: Follow the [Nuxt 3 Migration Guide](https://nuxt.com/docs/migration/overview)
   - **Breaking Changes**: Directory structure, configuration format, plugin system, module system
   - **Effort Estimate**: 3-5 days

2. **Vuex to Pinia**
   - **Complexity**: Medium
   - **Impact**: High
   - **Migration Path**: Follow the [Pinia Migration Guide](https://pinia.vuejs.org/cookbook/migration-vuex.html)
   - **Breaking Changes**: Store structure, no mutations, different access patterns
   - **Effort Estimate**: 2-3 days

3. **Apollo GraphQL Client**
   - **Complexity**: Medium
   - **Impact**: High
   - **Migration Path**: Update to Apollo Client 3.x and @nuxt/apollo module
   - **Breaking Changes**: API changes, cache configuration
   - **Effort Estimate**: 1-2 days

4. **Map Component Dependencies**
   - **Complexity**: Medium
   - **Impact**: High
   - **Migration Path**: Update Google Maps integration for Vue 3
   - **Breaking Changes**: Event handling, lifecycle hooks
   - **Effort Estimate**: 1-2 days

### Medium Priority Dependencies

These dependencies are important but have straightforward migration paths:

1. **UI Component Libraries**
   - **vue-slider-component**: Replace with @vueform/slider
   - **vue2-datepicker**: Replace with @vuepic/vue-datepicker
   - **v-tooltip**: Replace with floating-vue
   - **vue-star-rating**: Replace with vue3-star-rating
   - **Effort Estimate**: 2-3 days total

2. **Internationalization**
   - **nuxt-i18n**: Update to @nuxtjs/i18n v8
   - **@intlify/vue-i18n-loader**: Replace with @intlify/unplugin-vue-i18n
   - **Effort Estimate**: 1 day

3. **Development Tools**
   - **ESLint and related plugins**: Update to latest versions
   - **Tailwind CSS**: Update to latest version
   - **Effort Estimate**: 1 day

### Low Priority Dependencies

These dependencies are either framework-agnostic or have simple updates:

1. **Utility Libraries**
   - date-fns, dayjs, lodash, axios: Update to latest versions
   - **Effort Estimate**: 0.5 day

2. **Monitoring and Analytics**
   - Sentry, LogRocket: Update to Vue 3 compatible versions
   - **Effort Estimate**: 0.5 day

## Next Steps

1. ✅ Verify the complete list of dependencies from package.json
2. ✅ Research each dependency for Vue 3 compatibility
3. ✅ Document specific version recommendations
4. ✅ Identify high-risk dependencies
5. ✅ Create migration strategy for each dependency
6. ✅ Estimate effort for dependency updates
7. [ ] Evaluate Migration Build approach
8. [ ] Create a test project to validate key dependency migrations

## Research Notes

### Nuxt 3 Migration

Nuxt 3 represents a significant change from Nuxt 2, with many breaking changes:

- Built on Vue 3 and Vite
- New directory structure
- New composables system
- Changes to configuration format
- Different plugin system
- New module system

Key resources:
- [Nuxt 3 Migration Guide](https://nuxt.com/docs/migration/overview)
- [Nuxt 3 Documentation](https://nuxt.com/docs)

#### Migration Build Consideration

The Vue 3 Migration Build provides Vue 2 API compatibility with Vue 3 under the hood. For Nuxt, there's a similar concept called "Nuxt Bridge" which provides a migration path from Nuxt 2 to Nuxt 3.

**Pros of using Migration Build/Nuxt Bridge:**
- Allows incremental migration
- Reduces risk by allowing partial adoption
- Can help identify compatibility issues gradually

**Cons of using Migration Build/Nuxt Bridge:**
- Adds complexity to the migration process
- May introduce performance overhead
- Still requires eventual migration to full Vue 3/Nuxt 3 APIs

**Recommendation:** For OWSwims, given the moderate size of the application and the comprehensive nature of our migration plan, a direct migration approach with AI assistance is likely more efficient than using the Migration Build. However, we should keep this option in reserve if we encounter significant compatibility issues during the migration process.

### Vuex to Pinia Migration

Pinia is now the recommended state management solution for Vue 3:

- More intuitive API
- Better TypeScript support
- No mutations, just actions
- Simpler store structure
- Compatible with Vue DevTools

Key resources:
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Migrating from Vuex to Pinia](https://pinia.vuejs.org/cookbook/migration-vuex.html)

#### Migration Strategy

1. Create equivalent Pinia stores for each Vuex module
2. Convert getters to computed properties
3. Convert mutations and actions to actions
4. Update component access patterns
5. Test thoroughly to ensure state management works correctly

### Apollo GraphQL Migration

Apollo Client has undergone significant changes between versions 2.x and 3.x:

- New cache configuration
- Different import structure
- Changes to query components

Key resources:
- [Apollo Client Migration Guide](https://www.apollographql.com/docs/react/migrating/apollo-client-3-migration/)
- [Vue Apollo Documentation](https://v4.apollo.vuejs.org/)

## Component-Specific Considerations

### Map Component

The Map component is central to the application and will require special attention:

- Google Maps integration may need updates
- Event handling changes in Vue 3
- Ref handling differences
- Lifecycle hook changes

**Migration Strategy:**
1. Update lifecycle hooks (destroyed → unmounted, beforeDestroy → beforeUnmount)
2. Refactor refs usage to use the new ref() API
3. Update event handling to use the new emits option
4. Consider using the Composition API for better organization of map-related logic
5. Test thoroughly with different map interactions

### DaterangeSlider Component

Currently in active development and will need careful migration:

- vue2-datepicker replacement with @vuepic/vue-datepicker
- v-model changes in Vue 3 (prop and event names)
- Event handling differences

**Migration Strategy:**
1. Replace vue2-datepicker with @vuepic/vue-datepicker
2. Update v-model implementation to use the new syntax
3. Add explicit emits declaration
4. Test thoroughly with different date ranges and interactions

### Other Key Components

1. **EventPane.vue**
   - Update v-model usage
   - Update event handling
   - Consider refactoring to Composition API

2. **FilterBox.vue**
   - Update v-model usage
   - Update event handling
   - Consider refactoring to Composition API

3. **ReviewBox.vue**
   - Update star rating component
   - Update event handling

## Vue 3 Composition API Migration

For complex components, we recommend adopting the Composition API to improve code organization:

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

// After (Composition API with <script setup>)
<script setup>
import { ref, computed } from 'vue'

const locations = ref([])
const selectedLocation = ref(null)

const filteredLocations = computed(() => {
  // filtering logic
})

function selectLocation(location) {
  // selection logic
}
</script>
```

## Completion Checklist

- [x] Complete full dependency inventory
- [x] Research all dependencies for Vue 3 compatibility
- [x] Document specific version recommendations
- [x] Identify high-risk dependencies
- [x] Create migration strategy for each dependency
- [x] Estimate effort for dependency updates
- [ ] Prepare recommendation on Migration Build approach
- [ ] Create a test project to validate key dependency migrations
