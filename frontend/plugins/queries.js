import gql from 'graphql-tag'
import { formatISO } from 'date-fns'

export default ({ app }, inject) => {
  inject('queries', {
    location(locationId, keyword, dateRange) {
      const client = app.apolloProvider.defaultClient
      return client.query({
        fetchPolicy: 'no-cache', // allow to refetch when reviews are updated
        query: gql`
          query ($dateFrom: Date!, $dateTo: Date!, $locationId: ID!) {
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
  })
}
