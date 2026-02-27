import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { addMonths } from 'date-fns'

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
  }
})
