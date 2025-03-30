import { gql } from '@apollo/client/core'
import { formatISO } from 'date-fns'

// This plugin is updated for Vue 3/Nuxt 3 and Apollo Client 3.x
export default defineNuxtPlugin((nuxtApp) => {
  // Define GraphQL queries
  const queries = {
    location(locationId, keyword, dateRange) {
      // Get the Apollo client from the nuxtApp
      const client = nuxtApp.$apollo.defaultClient

      return client.query({
        fetchPolicy: 'no-cache', // allow to refetch when reviews are updated
        query: gql`
          query($dateFrom: Date!, $dateTo: Date!, $locationId: ID!) {
            location(id: $locationId) {
              id
              country
              city
              headerPhoto
              lat
              lng
              waterType
              waterName
              averageRating
            }
            allEvents(
              dateFrom: $dateFrom
              dateTo: $dateTo
              location: $locationId
            ) {
              edges {
                node {
                  id
                  slug
                  name
                  dateStart
                  dateEnd
                  flyerImage
                  website
                  description
                  needsMedicalCertificate
                  needsLicense
                  soldOut
                  cancelled
                  withRanking
                  waterTemp
                  organizer {
                    name
                    website
                    logo
                  }
                  reviews {
                    edges {
                      node {
                        id
                        createdAt
                        rating
                        comment
                        country
                        name
                      }
                    }
                  }
                  races {
                    edges {
                      node {
                        id
                        distance
                        date
                        raceTime
                        name
                        distance
                        wetsuit
                        priceValue
                        coordinates
                      }
                    }
                  }
                }
              }
            }
          }
        `,
        variables: {
          locationId,
          keyword,
          dateFrom: formatISO(dateRange[0], {
            representation: 'date',
          }),
          dateTo: formatISO(dateRange[1], {
            representation: 'date',
          }),
        },
      })
    },
  }

  // Provide the queries to the app
  nuxtApp.provide('queries', queries)

  // For backward compatibility with Vue 2 code
  nuxtApp.vueApp.config.globalProperties.$queries = queries
})
