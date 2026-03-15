import {
  ApolloClient,
  InMemoryCache,
  createHttpLink,
  ApolloLink,
} from '@apollo/client/core'
import { DefaultApolloClient } from '@vue/apollo-composable'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()

  const httpLink = createHttpLink({
    uri: config.public.graphqlEndpoint,
    credentials: 'omit',
  })

  const authLink = new ApolloLink((operation, forward) => {
    if (import.meta.client) {
      const token = localStorage.getItem('apollo-token')
      if (token) {
        operation.setContext({
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      }
    }
    return forward(operation)
  })

  const cache = new InMemoryCache()

  const apolloClient = new ApolloClient({
    link: authLink.concat(httpLink),
    cache,
  })

  nuxtApp.vueApp.provide(DefaultApolloClient, apolloClient)

  return {
    provide: {
      apollo: apolloClient,
    },
  }
})
