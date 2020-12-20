import gql from 'graphql-tag'
import { addMonths, formatISO } from 'date-fns'

export const state = () => ({
  lat: null,
  lng: null,
  pickedLocationId: null,
  distanceRange: [0, 30],
  dateRange: [0, 12],
  pickedLocationData: null,
})

export const mutations = {
  mylocation(s, latlng) {
    s.lat = latlng.lat
    s.lng = latlng.lng
  },
  pickedLocationId(s, id) {
    s.pickedLocationId = id
    console.log(s)

    const client = this.app.apolloProvider.defaultClient
    client
      .query({
        query: gql`
          query(
            $distanceFrom: Float!
            $distanceTo: Float!
            $dateFrom: Date!
            $dateTo: Date!
            $locationId: ID!
          ) {
            allEvents(
              dateFrom: $dateFrom
              dateTo: $dateTo
              location: $locationId
            ) {
              edges {
                node {
                  id
                  name
                  dateStart
                  dateEnd
                  website
                  races(
                    distance_Gte: $distanceFrom
                    distance_Lte: $distanceTo
                  ) {
                    edges {
                      node {
                        distance
                        date
                        raceTime
                        name
                        distance
                        wetsuit
                        priceValue
                      }
                    }
                  }
                }
              }
            }
          }
        `,
        variables: {
          locationId: s.pickedLocationId,
          distanceFrom: s.distanceRange[0],
          distanceTo: s.distanceRange[1],
          dateFrom: formatISO(addMonths(new Date(), s.dateRange[0]), {
            representation: 'date',
          }),
          dateTo: formatISO(addMonths(new Date(), s.dateRange[1]), {
            representation: 'date',
          }),
        },
      })
      .then((result) => this.commit('pickedLocationData', result.data))
  },
  pickedLocationData(s, data) {
    s.pickedLocationData = data
  },
  distanceRange(s, id) {
    s.distanceRange = id
  },
  dateRange(s, id) {
    s.dateRange = id
  },
}

export const getters = {
  mylocation(s) {
    return {
      lat: s.lat,
      lng: s.lng,
    }
  },
  pickedLocationId(s) {
    return s.pickedLocationId
  },
  distanceRange(s) {
    return s.distanceRange
  },
  dateRange(s) {
    return s.dateRange
  },
  pickedLocationData(s) {
    return s.pickedLocationData
  },
}
