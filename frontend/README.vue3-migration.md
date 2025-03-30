# Vue 3 Migration - Frontend

This document provides information about the Vue 3 migration process for the OWSwims frontend.

## Current Status

We have begun the migration process by creating a Nuxt 3 configuration file (`nuxt.config.ts`) based on the existing Nuxt 2 configuration. This file will be used once the project is migrated to Nuxt 3.

## Nuxt 3 Configuration

The new Nuxt 3 configuration file (`nuxt.config.ts`) has been created with the following changes from the Nuxt 2 configuration:

1. **Format Changes**:
   - Changed from JavaScript (`.js`) to TypeScript (`.ts`)
   - Updated configuration structure to match Nuxt 3 requirements
   - Moved head configuration to `app.head`
   - Replaced `env` with `runtimeConfig.public`

2. **Module Updates**:
   - Added `@pinia/nuxt` for state management (replacing Vuex)
   - Updated Apollo configuration for Nuxt 3
   - Updated i18n configuration for Nuxt 3

3. **Component Dependencies**:
   - Added CSS imports for Vue 3 compatible UI components:
     - `@vueform/slider` (replacing `vue-slider-component`)
     - `@vuepic/vue-datepicker` (replacing `vue2-datepicker`)
     - `floating-vue` (replacing `v-tooltip`)

4. **Build Configuration**:
   - Added transpile options for Vue 3 compatible components
   - Added Vite configuration section (new in Nuxt 3)

## Known Issues

The TypeScript and ESLint errors in the Nuxt 3 configuration file are expected at this stage since the project is still using Nuxt 2. These errors will be resolved once the project dependencies are updated to Nuxt 3.

## Next Steps

1. **Update package.json**:
   - Add Nuxt 3 and related dependencies
   - Update or replace Vue 2 specific dependencies with Vue 3 compatible alternatives
   - Update development dependencies

2. **Migrate Vuex to Pinia**:
   - Create Pinia store structure
   - Convert Vuex modules to Pinia stores
   - Update store access patterns in components

3. **Update Apollo Client**:
   - Migrate to Apollo Client 3.x
   - Update GraphQL queries and mutations

4. **Update Directory Structure**:
   - Adjust directory structure to match Nuxt 3 conventions if needed
   - Update imports and references accordingly

5. **Migrate Components**:
   - Start with shared components
   - Update lifecycle hooks (e.g., `destroyed` → `unmounted`)
   - Update template syntax for v-model changes
   - Consider using Composition API for complex components

## Resources

- [Nuxt 3 Migration Guide](https://nuxt.com/docs/migration/overview)
- [Vue 3 Migration Guide](https://v3-migration.vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Vue 3 Composition API Documentation](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Apollo Client Migration Guide](https://www.apollographql.com/docs/react/migrating/apollo-client-3-migration/)

## Migration Tracking

For detailed information about the migration progress, refer to:
- [Migration Plan](../migration_plan.md)
- [Migration Tracker](../vue3-migration/migration-tracker.md)
- [Dependency Analysis](../vue3-migration/dependency-analysis.md)
