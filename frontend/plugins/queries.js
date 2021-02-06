import gql from 'graphql-tag'
import { addMonths, formatISO } from 'date-fns'

export default ({ app }, inject) => {
  inject('queries', {
    location(locationId, keyword, dateRange) {
      const client = app.apolloProvider.defaultClient
      return client.query({
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
          dateFrom: formatISO(addMonths(new Date(), dateRange[0]), {
            representation: 'date',
          }),
          dateTo: formatISO(addMonths(new Date(), dateRange[1]), {
            representation: 'date',
          }),
        },
      })
    },
  })
}
