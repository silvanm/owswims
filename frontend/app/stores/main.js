import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { addMonths, formatISO } from 'date-fns'
import gql from 'graphql-tag'

export const useMainStore = defineStore('main', () => {
  // State
  const lat = ref(null)
  const lng = ref(null)
  const isAccurate = ref(false)
  const countryCode = ref(null)
  const pickedLocationId = ref(null)
  const pickedLocationZoomedIn = ref(null)
  const keyword = ref('')
  const organizerData = ref(null)
  const isEmbedded = ref(false)
  const mapType = ref(false)
  const showOrganizerLogo = ref(false)
  const distanceRange = ref([0, 1000])
  const dateRange = ref([new Date(), addMonths(new Date(), 12)])
  const pickedLocationData = ref(null)
  const focusedEventId = ref(null)
  const travelTimes = ref([])
  const isLoading = ref(false)
  const justMounted = ref(true)
  const raceTrackUnderEditId = ref(null)
  const raceTrackUnderFocusId = ref(null)
  const raceTrackUnderHoverId = ref(null)
  const raceTrackDeletedId = ref(null)
  const pageTitle = ref(null)
  const reviewBoxShown = ref(false)
  const submitEventBoxShown = ref(false)
  const activeInfoTab = ref(null)

  // Getters
  const mylocation = computed(() => ({
    isAccurate: isAccurate.value,
    latlng: {
      lat: lat.value,
      lng: lng.value,
    },
  }))

  // Actions
  async function locateMe() {
    isLoading.value = true
    try {
      const position = await new Promise((resolve, reject) =>
        navigator.geolocation.getCurrentPosition(resolve, reject)
      )
      lat.value = position.coords.latitude
      lng.value = position.coords.longitude
      isAccurate.value = true
    } finally {
      isLoading.value = false
    }
  }

  function setMylocation(data) {
    lat.value = data.latlng.lat
    lng.value = data.latlng.lng
    isAccurate.value = data.isAccurate
  }

  async function fetchPickedLocationData(locationId) {
    pickedLocationData.value = null
    const { $apollo } = useNuxtApp()
    const result = await $apollo.query({
      fetchPolicy: 'no-cache',
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
          allEvents(dateFrom: $dateFrom, dateTo: $dateTo, location: $locationId) {
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
        dateFrom: formatISO(dateRange.value[0], { representation: 'date' }),
        dateTo: formatISO(dateRange.value[1], { representation: 'date' }),
      },
    })
    pickedLocationData.value = result.data
  }

  return {
    // State
    lat,
    lng,
    isAccurate,
    countryCode,
    pickedLocationId,
    pickedLocationZoomedIn,
    keyword,
    organizerData,
    isEmbedded,
    mapType,
    showOrganizerLogo,
    distanceRange,
    dateRange,
    pickedLocationData,
    focusedEventId,
    travelTimes,
    isLoading,
    justMounted,
    raceTrackUnderEditId,
    raceTrackUnderFocusId,
    raceTrackUnderHoverId,
    raceTrackDeletedId,
    pageTitle,
    reviewBoxShown,
    submitEventBoxShown,
    activeInfoTab,

    // Getters
    mylocation,

    // Actions
    locateMe,
    setMylocation,
    fetchPickedLocationData,
  }
})
