import gql from 'graphql-tag'
import { addMonths, formatISO } from 'date-fns'
// import calculateDistance from '@assets/js/calculateDistance'

export const state = () => ({
  lat: null,
  lng: null,
  isAccurate: false,
  pickedLocationId: null,
  distanceRange: [0, 30],
  dateRange: [0, 12],
  pickedLocationData: null,
  travelTimes: [],
  isLoading: false,
})

export const mutations = {
  mylocation(s, data) {
    s.lat = data.latlng.lat
    s.lng = data.latlng.lng
    s.isAccurate = data.isAccurate
  },
  pickedLocationId(s, id) {
    s.pickedLocationId = id
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
            location(id: $locationId) {
              country
              city
              headerPhoto
              lat
              lng
            }
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
                  description
                  needsMedicalCertificate
                  needsLicense
                  soldOut
                  cancelled
                  withRanking
                  waterTemp
                  waterType
                  organizer {
                    name
                    website
                  }
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
  travelTimes(s, id) {
    s.travelTimes = id
  },
  isLoading(s, isLoading) {
    s.isLoading = isLoading
  },
}

export const getters = {
  mylocation(s) {
    return {
      isAccurate: s.isAccurate,
      latlng: {
        lat: s.lat,
        lng: s.lng,
      },
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
  travelTimes(s) {
    return s.travelTimes
  },
  isLoading(s) {
    return s.isLoading
  },
}
