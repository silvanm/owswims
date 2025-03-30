# Apollo Client 3.x Migration Guide

This document outlines the migration of the OWSwims GraphQL integration from Apollo Client 2.x to Apollo Client 3.x as part of the Vue 3/Nuxt 3 migration.

## Overview

Apollo Client 3.x brings several improvements and changes compared to Apollo Client 2.x:

- Improved performance and bundle size
- Better TypeScript support
- Unified cache architecture
- Simplified API
- Better error handling

## Dependencies

The following dependencies have been added to support Apollo Client 3.x:

```json
{
  "dependencies": {
    "@apollo/client": "^3.8.10",
    "@vue/apollo-composable": "^4.0.0-beta.12",
    "graphql": "^16.8.1",
    "nuxt-apollo": "^5.0.0"
  },
  "devDependencies": {
    "@types/graphql": "^14.5.0"
  }
}
```

To install these dependencies, run:

```bash
npm install @apollo/client@^3.8.10 @vue/apollo-composable@^4.0.0-beta.12 graphql@^16.8.1 nuxt-apollo@^5.0.0
npm install --save-dev @types/graphql@^14.5.0
```

## Configuration

### Nuxt Configuration

The Apollo Client is configured in `nuxt.config.ts`:

```typescript
// Apollo module configuration
apollo: {
  clients: {
    default: {
      // Use the environment variable from runtimeConfig
      httpEndpoint: process.env.GRAPHQL_ENDPOINT,
      // You can add more configuration options here as needed
      inMemoryCacheOptions: {
        // Configure the InMemoryCache options
      },
      defaultOptions: {
        // Configure default options for queries and mutations
        watchQuery: {
          fetchPolicy: 'cache-and-network',
        },
        query: {
          fetchPolicy: 'network-only',
        },
      },
    },
  },
},

// Build configuration
build: {
  transpile: [
    // Other dependencies
    '@apollo/client',
    'ts-invariant',
    'graphql',
  ],
},
```

### Apollo Plugin

A new Apollo plugin has been created at `plugins/apollo.js` to set up the Apollo Client:

```javascript
// Apollo Client 3.x plugin for Vue 3/Nuxt 3
import {
  ApolloClient,
  InMemoryCache,
  createHttpLink,
} from '@apollo/client/core'
import { provideApolloClient } from '@vue/apollo-composable'

export default defineNuxtPlugin((nuxtApp) => {
  const runtimeConfig = useRuntimeConfig()
  const httpEndpoint =
    runtimeConfig.public.apollo?.clients?.default?.httpEndpoint || '/graphql'

  // Create the apollo client
  const httpLink = createHttpLink({
    uri: httpEndpoint,
  })

  const cache = new InMemoryCache()

  const apolloClient = new ApolloClient({
    link: httpLink,
    cache,
    defaultOptions: {
      query: {
        fetchPolicy: 'no-cache', // Default fetch policy
      },
    },
  })

  // Provide the apollo client to the app
  provideApolloClient(apolloClient)

  // Make apollo client available in the app
  nuxtApp.provide('apollo', {
    defaultClient: apolloClient,
  })

  // For backward compatibility with Vue 2 code
  nuxtApp.vueApp.config.globalProperties.$apollo = {
    query: (options) => apolloClient.query(options),
    mutate: (options) => apolloClient.mutate(options),
    getClient: () => apolloClient,
  }
})
```

## Usage

### Option 1: Using the Composition API (Recommended)

For new components or when refactoring existing components, use the Composition API with the `useQuery` and `useMutation` composables:

```vue
<script setup>
import { useQuery } from '@vue/apollo-composable'
import { gql } from '@apollo/client/core'

// Define the query
const LOCATION_QUERY = gql`
  query GetLocation($id: ID!) {
    location(id: $id) {
      id
      name
      city
      country
    }
  }
`

// Use the query
const { result, loading, error } = useQuery(LOCATION_QUERY, {
  id: '1',
})

// Access the data
const location = computed(() => result.value?.location)
</script>
```

### Option 2: Using the Queries Plugin (Backward Compatibility)

For backward compatibility, the `queries.js` plugin has been updated to work with Apollo Client 3.x:

```javascript
// In a component
export default {
  methods: {
    async fetchLocation() {
      try {
        const result = await this.$queries.location(
          '1',
          '',
          [new Date(), new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)]
        )
        this.locationData = result.data
      } catch (error) {
        console.error('Error fetching location:', error)
      }
    }
  }
}
```

### Option 3: Direct Apollo Client Access

You can also access the Apollo Client directly:

```javascript
// In a component
export default {
  methods: {
    async fetchLocation() {
      try {
        const result = await this.$apollo.query({
          query: gql`
            query GetLocation($id: ID!) {
              location(id: $id) {
                id
                name
                city
                country
              }
            }
          `,
          variables: {
            id: '1',
          },
        })
        this.locationData = result.data
      } catch (error) {
        console.error('Error fetching location:', error)
      }
    }
  }
}
```

## Testing

A test component has been created at `components/ApolloTest.vue` to verify that the Apollo Client 3.x integration works correctly. This component demonstrates how to use the Apollo Client with the Composition API.

## Migration Steps

1. Install the required dependencies
2. Update the Nuxt configuration
3. Create the Apollo plugin
4. Update the queries plugin
5. Test the integration with the ApolloTest component
6. Gradually migrate components to use the Composition API

## Common Issues and Solutions

### Error: Cannot read property 'defaultClient' of undefined

This error occurs when trying to access the Apollo client before it's initialized. Make sure you're accessing the client after the plugin has been loaded.

### Error: No ApolloClient found in your Vue app

This error occurs when the Apollo client hasn't been properly provided to the Vue app. Make sure the Apollo plugin is correctly set up and loaded.

### Error: Network error: Failed to fetch

This error occurs when the GraphQL endpoint is not accessible. Check that the `GRAPHQL_ENDPOINT` environment variable is correctly set and that the GraphQL server is running.

## Resources

- [Apollo Client Documentation](https://www.apollographql.com/docs/react/)
- [Vue Apollo Documentation](https://v4.apollo.vuejs.org/)
- [Nuxt Apollo Module Documentation](https://apollo.nuxtjs.org/)
