# Pinia Stores

This directory contains the Pinia stores for the OWSwims application. These stores replace the Vuex stores that were used in the Vue 2 version of the application.

## Migration from Vuex to Pinia

The migration from Vuex to Pinia involves the following changes:

1. **Store Structure**:
   - Vuex: `store/index.js` and `store/auth.js`
   - Pinia: `stores/main.js` and `stores/auth.js`

2. **API Changes**:
   - Mutations and actions in Vuex are combined into actions in Pinia
   - Getters in Pinia receive the state as the first argument
   - State is directly modifiable in Pinia actions (no need for mutations)

3. **Usage in Components**:
   - Vuex: `this.$store.state.x`, `this.$store.getters.x`, `this.$store.commit('x')`, `this.$store.dispatch('x')`
   - Pinia: `store.x`, `store.x`, `store.x()`, `store.x()`

## Store Overview

### Main Store (`main.js`)

The main store contains the application state related to:
- User location
- Map state
- Selected locations and events
- Filters (keyword, distance, date)
- UI state (loading, modals, etc.)

### Auth Store (`auth.js`)

The auth store handles user authentication:
- Login/logout functionality
- User state
- Authentication token management

## Usage in Vue 3 Components

```javascript
// Options API
import { useMainStore } from '~/stores/main'
import { useAuthStore } from '~/stores/auth'

export default {
  setup() {
    const mainStore = useMainStore()
    const authStore = useAuthStore()
    
    return {
      mainStore,
      authStore
    }
  },
  
  methods: {
    someMethod() {
      // Access state
      console.log(this.mainStore.keyword)
      
      // Call actions
      this.mainStore.setKeyword('swimming')
      this.authStore.logout()
    }
  }
}
```

```javascript
// Composition API with <script setup>
<script setup>
import { useMainStore } from '~/stores/main'
import { useAuthStore } from '~/stores/auth'

const mainStore = useMainStore()
const authStore = useAuthStore()

// Access state
console.log(mainStore.keyword)

// Call actions
function updateKeyword(keyword) {
  mainStore.setKeyword(keyword)
}
</script>
```

## Notes for Migration

1. **Apollo Client Integration**:
   - The stores currently use `useNuxtApp().$queries` which will need to be updated to use Apollo Client 3.x
   - This will be addressed in the Apollo Client migration phase

2. **Router Integration**:
   - The stores currently use `useNuxtApp().$urlHistory` which will need to be updated to use Vue Router 4.x
   - This will be addressed in the router migration phase

3. **Plugin Access**:
   - Plugins are accessed via `useNuxtApp().$pluginName` instead of `this.$pluginName`
   - This pattern is used throughout the stores

## Future Improvements

1. **Composition API**:
   - Consider refactoring complex store logic into composables
   - This can improve code organization and reusability

2. **TypeScript**:
   - Add TypeScript type definitions for better type safety
   - Pinia has excellent TypeScript support

3. **Store Modules**:
   - Consider splitting the main store into smaller, more focused stores
   - This can improve maintainability and performance
