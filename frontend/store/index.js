export const state = () => ({
  lat: null,
  lng: null,
  isAccurate: false,
  pickedLocationId: null,
  pickedLocationZoomedIn: null,
  keyword: '',
  organizerData: null, // set if we have a organizer-filter applied (for an embedded map)
  isEmbedded: false,
  mapType: false,
  showOrganizerLogo: false,
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
    const p = this.$queries.location(s.pickedLocationId, s.keyword, s.dateRange)
    p.then((result) => this.commit('pickedLocationData', result.data))
  },
  pickedLocationData(s, data) {
    // if there is only one event, then use the slug of this event
    const query = { ...this.$router.currentRoute.query }

    if (data.allEvents.edges.length === 1) {
      query.event = data.allEvents.edges[0].node.slug
    } else {
      query.location = data.allEvents.edges[0].node.slug
    }
    this.$router.push({
      path: '',
      query,
    })

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
  mapType(s, mapType) {
    s.mapType = mapType
  },
  showOrganizerLogo(s, mapType) {
    s.showOrganizerLogo = mapType
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
  mapType(s) {
    return s.mapType
  },
  showOrganizerLogo(s) {
    return s.showOrganizerLogo
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
