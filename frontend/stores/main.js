// stores/main.js
import { defineStore } from 'pinia'
import { addMonths } from 'date-fns'
import { useNuxtApp } from '#app'

export const useMainStore = defineStore('main', {
  state: () => ({
    lat: null,
    lng: null,
    isAccurate: false,
    countryCode: null,
    pickedLocationId: null,
    pickedLocationZoomedIn: null,
    keyword: '',
    organizerData: null, // set if we have a organizer-filter applied (for an embedded map)
    isEmbedded: false,
    mapType: false,
    showOrganizerLogo: false,
    distanceRange: [0, 1000],
    dateRange: [new Date(), addMonths(new Date(), 12)],
    pickedLocationData: null,
    focusedEventId: null,
    travelTimes: [],
    isLoading: false,
    justMounted: true, // used to hide elements which should disappear after some time
    raceTrackUnderEditId: null,
    raceTrackUnderFocusId: null,
    raceTrackUnderHoverId: null,
    raceTrackDeletedId: null,
    pageTitle: null,
    reviewBoxShown: false,
  }),

  getters: {
    mylocation: (state) => ({
      isAccurate: state.isAccurate,
      latlng: {
        lat: state.lat,
        lng: state.lng,
      },
    }),
    countryCode: (state) => state.countryCode,
    pickedLocationId: (state) => state.pickedLocationId,
    keyword: (state) => state.keyword,
    distanceRange: (state) => state.distanceRange,
    dateRange: (state) => state.dateRange,
    pickedLocationData: (state) => state.pickedLocationData,
    pickedLocationZoomedIn: (state) => state.pickedLocationZoomedIn,
    focusedEventId: (state) => state.focusedEventId,
    travelTimes: (state) => state.travelTimes,
    organizerData: (state) => state.organizerData,
    isEmbedded: (state) => state.isEmbedded,
    mapType: (state) => state.mapType,
    showOrganizerLogo: (state) => state.showOrganizerLogo,
    isLoading: (state) => state.isLoading,
    justMounted: (state) => state.justMounted,
    raceTrackUnderEditId: (state) => state.raceTrackUnderEditId,
    raceTrackUnderFocusId: (state) => state.raceTrackUnderFocusId,
    raceTrackUnderHoverId: (state) => state.raceTrackUnderHoverId,
    raceTrackDeletedId: (state) => state.raceTrackDeletedId,
    pageTitle: (state) => state.pageTitle,
    reviewBoxShown: (state) => state.reviewBoxShown,
  },

  actions: {
    // Mutations from Vuex are now actions in Pinia
    setMyLocation(data) {
      this.lat = data.latlng.lat
      this.lng = data.latlng.lng
      this.isAccurate = data.isAccurate
    },
    setCountryCode(data) {
      this.countryCode = data
    },
    setPickedLocationId(id) {
      this.pickedLocationId = id
      // Note: This will need to be updated to use the new Apollo Client 3.x
      // and injected services pattern instead of this.$queries
      const queries = useNuxtApp().$queries
      const p = queries.location(
        this.pickedLocationId,
        this.keyword,
        this.dateRange
      )
      p.then((result) => this.setPickedLocationData(result.data))
    },
    setPickedLocationData(data) {
      // Code Smell!
      // if there is only one event, then use the slug of this event
      const locationStr = `${data.location.city}, ${data.location.country}`

      // Note: This will need to be updated to use the new router and URL history pattern
      // instead of this.$urlHistory
      const urlHistory = useNuxtApp().$urlHistory
      const gtag = useNuxtApp().$gtag

      if (data.allEvents.edges.length === 1) {
        urlHistory.push({}, `/event/${data.allEvents.edges[0].node.slug}`)
        this.pageTitle = `open-water-swims.com - ${data.allEvents.edges[0].node.name}, ${locationStr}`
      } else {
        urlHistory.push({ location: data.location.id }, '')
        this.pageTitle = `open-water-swims.com - ${locationStr}`
      }

      gtag('event', 'eventView', {
        event_label: data.allEvents.edges[0].node.slug,
      })

      this.pickedLocationData = data
    },
    setPickedLocationZoomedIn(data) {
      this.pickedLocationZoomedIn = data
    },
    setFocusedEventId(data) {
      this.focusedEventId = data
      const gtag = useNuxtApp().$gtag
      gtag('event', 'eventView', {
        event_label: data.slug,
      })
    },
    setKeyword(keyword) {
      this.keyword = keyword
    },
    setDistanceRange(range) {
      this.distanceRange = range
    },
    setDateRange(range) {
      this.dateRange = range
    },
    setTravelTimes(times) {
      this.travelTimes = times
    },
    setOrganizerData(data) {
      this.organizerData = data
    },
    setIsEmbedded(isEmbedded) {
      this.isEmbedded = isEmbedded
    },
    setMapType(mapType) {
      this.mapType = mapType
    },
    setShowOrganizerLogo(show) {
      this.showOrganizerLogo = show
    },
    setIsLoading(isLoading) {
      this.isLoading = isLoading
    },
    setJustMounted(justMounted) {
      this.justMounted = justMounted
    },
    setRaceTrackUnderEditId(id) {
      this.raceTrackUnderEditId = id
    },
    setRaceTrackUnderFocusId(id) {
      this.raceTrackUnderFocusId = id
    },
    setRaceTrackUnderHoverId(id) {
      this.raceTrackUnderHoverId = id
    },
    setRaceTrackDeletedId(id) {
      this.raceTrackDeletedId = id
    },
    setReviewBoxShown(shown) {
      this.reviewBoxShown = shown
    },

    // Actions from Vuex remain actions in Pinia
    async locateMe() {
      this.isLoading = true

      function getPosition(options) {
        return new Promise((resolve, reject) =>
          navigator.geolocation.getCurrentPosition(resolve, reject, options)
        )
      }

      const position = await getPosition()

      this.setMyLocation({
        isAccurate: true,
        latlng: {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        },
      })
      this.isLoading = false
    },

    refreshLocationData() {
      // Note: This will need to be updated to use the new Apollo Client 3.x
      // and injected services pattern instead of this.$queries
      const queries = useNuxtApp().$queries
      const p = queries.location(
        this.pickedLocationId,
        this.keyword,
        this.dateRange
      )
      p.then((result) => this.setPickedLocationData(result.data))
    },
  },
})
