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
