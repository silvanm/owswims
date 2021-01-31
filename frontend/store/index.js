import gql from 'graphql-tag'
import { addMonths, formatISO } from 'date-fns'
// import calculateDistance from '@assets/js/calculateDistance'

export const state = () => ({
  lat: null,
  lng: null,
  isAccurate: false,
  pickedLocationId: null,
  pickedLocationZoomedIn: null,
  keyword: '',
  organizerData: null,
  isEmbedded: false,
  distanceRange: [0, 30],
  dateRange: [0, 12],
  pickedLocationData: null,
  focusedEventId: null,
  travelTimes: [],
  isLoading: false,
  raceTrackUnderEditId: null,
  raceTrackUnderFocusId: null,
  raceTrackUnderHoverId: null,
  raceTrackDeletedId: null,
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
                  races(
                    distance_Gte: $distanceFrom
                    distance_Lte: $distanceTo
                  ) {
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
          locationId: s.pickedLocationId,
          keyword: s.keyword,
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
    // if there is only one event, then use the slug of this event
    if (data.allEvents.edges.length === 1) {
      history.pushState(
        {},
        data.allEvents.edges[0].node.name,
        `?event=` + encodeURIComponent(data.allEvents.edges[0].node.slug)
      )
    } else {
      history.pushState(
        {},
        `${data.location.city}, ${data.location.country}`,
        `?location=` + encodeURIComponent(s.pickedLocationId)
      )
    }
    s.pickedLocationData = data
  },
  pickedLocationZoomedIn(s, data) {
    s.pickedLocationZoomedIn = data
  },
  focusedEventId(s, data) {
    s.focusedEventId = data
  },
  keyword(s, keyword) {
    s.keyword = keyword
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
  organizerData(s, id) {
    s.organizerData = id
  },
  isEmbedded(s, isEmbedded) {
    s.isEmbedded = isEmbedded
  },
  isLoading(s, isLoading) {
    s.isLoading = isLoading
  },
  raceTrackUnderEditId(s, raceTrackUnderEditId) {
    s.raceTrackUnderEditId = raceTrackUnderEditId
  },
  raceTrackUnderFocusId(s, raceTrackUnderFocusId) {
    s.raceTrackUnderFocusId = raceTrackUnderFocusId
  },
  raceTrackUnderHoverId(s, raceTrackUnderHoverId) {
    s.raceTrackUnderHoverId = raceTrackUnderHoverId
  },
  raceTrackDeletedId(s, raceTrackDeletedId) {
    s.raceTrackDeletedId = raceTrackDeletedId
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
  keyword(s) {
    return s.keyword
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
  pickedLocationZoomedIn(s) {
    return s.pickedLocationZoomedIn
  },
  focusedEventId(s) {
    return s.focusedEventId
  },
  travelTimes(s) {
    return s.travelTimes
  },
  organizerData(s) {
    return s.organizerData
  },
  isEmbedded(s) {
    return s.isEmbedded
  },
  isLoading(s) {
    return s.isLoading
  },
  raceTrackUnderEditId(s) {
    return s.raceTrackUnderEditId
  },
  raceTrackUnderFocusId(s) {
    return s.raceTrackUnderFocusId
  },
  raceTrackUnderHoverId(s) {
    return s.raceTrackUnderHoverId
  },
  raceTrackDeletedId(s) {
    return s.raceTrackDeletedId
  },
}

export const actions = {
  async locateMe(context) {
    context.commit('isLoading', true)

    function getPosition(options) {
      return new Promise((resolve, reject) =>
        navigator.geolocation.getCurrentPosition(resolve, reject, options)
      )
    }

    const position = await getPosition()

    context.commit('mylocation', {
      isAccurate: true,
      latlng: {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      },
    })
    context.commit('isLoading', false)
  },
}
