<template>
  <div>
    <!-- Bottom-left corner ribbon for event submission -->
    <div
      v-if="!store.isEmbedded && !store.pickedLocationId"
      class="submit-ribbon"
      @click="store.submitEventBoxShown = true"
    >
      <span>{{ t('submitYourEvent') }}</span>
    </div>

    <WelcomeBox
      v-if="
        welcomeboxShown &&
        !store.pickedLocationId &&
        !store.isEmbedded &&
        !store.showOrganizerLogo
      "
      @hide="hideWelcomeBox()"
    />
    <ReviewBox
      v-if="store.reviewBoxShown"
      @hide="store.reviewBoxShown = false"
    />
    <SubmitEventBox
      v-if="store.submitEventBoxShown"
      @hide="store.submitEventBoxShown = false"
    />
    <div
      v-if="
        store.organizerData &&
        !store.pickedLocationId &&
        !useDevice().isMobile() &&
        store.showOrganizerLogo
      "
      class="p-4"
    >
      <OrganizerLogo
        :image="store.organizerData.logo"
        :url="store.organizerData.website"
      />
    </div>
    <div class="xl:m-4">
      <LoginBox
        v-if="loginboxShown && !authStore.loggedIn"
        @hide="doHideLogin"
      />
      <ClientOnly>
        <Map
          v-if="locationsFiltered"
          ref="mapRef"
          :locations="locationsFiltered"
          :lat="store.lat"
          :lng="store.lng"
          :distance-from="store.distanceRange[0]"
          :distance-to="store.distanceRange[1]"
          :date-range="store.dateRange"
          @location-picked="locationPicked()"
        />
      </ClientOnly>
      <Spinner :show="store.isLoading" />
      <div style="max-height: 100vh">
        <FilterBox
          v-if="!store.isEmbedded"
          ref="filterboxRef"
          @show-login="doShowLogin"
        />
        <EventPane v-if="store.pickedLocationId" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted } from 'vue'
import gql from 'graphql-tag'
import { useQuery } from '@vue/apollo-composable'
import { formatISO } from 'date-fns'
import axios from 'axios'

const { t } = useI18n()
const store = useMainStore()
const authStore = useAuthStore()
const config = useRuntimeConfig()

const mapRef = ref(null)
const filterboxRef = ref(null)
const loginboxShown = ref(false)
const welcomeboxShown = ref(false)

const LOCATIONS_QUERY = gql`
  query (
    $keyword: String!
    $distanceFrom: Float!
    $distanceTo: Float!
    $dateFrom: Date!
    $dateTo: Date!
    $organizerSlug: String!
    $organizerId: ID!
  ) {
    locationsFiltered(
      keyword: $keyword
      raceDistanceGte: $distanceFrom
      raceDistanceLte: $distanceTo
      dateFrom: $dateFrom
      dateTo: $dateTo
      organizerSlug: $organizerSlug
      organizerId: $organizerId
    ) {
      id
      country
      city
      lat
      lng
      averageRating
    }
  }
`

const queryVariables = computed(() => ({
  keyword: store.keyword,
  distanceFrom: store.distanceRange[0],
  distanceTo: store.distanceRange[1],
  dateFrom: formatISO(store.dateRange[0], { representation: 'date' }),
  dateTo: formatISO(store.dateRange[1], { representation: 'date' }),
  organizerSlug: store.organizerData ? store.organizerData.slug : '',
  organizerId: store.organizerData ? store.organizerData.id : '',
}))

const { result: locationsResult } = useQuery(LOCATIONS_QUERY, queryVariables)

const previousLocations = shallowRef(null)
const locationsFiltered = computed(() => {
  const current = locationsResult.value?.locationsFiltered
  if (current) {
    previousLocations.value = current
  }
  return current ?? previousLocations.value
})

// Google Maps script injection
useHead({
  title: computed(() => store.pageTitle ?? t('pageTitle')),
  script: [
    {
      src: `https://maps.googleapis.com/maps/api/js?key=${config.public.googleMapsKey}&libraries=drawing&callback=initGoogleMaps`,
      async: true,
      defer: true,
    },
  ],
})

// Initialize Google Maps callback handler
if (import.meta.client) {
  window.googleMapsReady = false
  window.initGoogleMaps = function () {
    window.googleMapsReady = true
    window.dispatchEvent(new Event('google-maps-ready'))
  }
}

onMounted(async () => {
  // detect coarse position via IP
  try {
    const response = await axios.post(
      'https://www.googleapis.com/geolocation/v1/geolocate?key=' +
        config.public.googleMapsKey,
      { considerIp: 'true' }
    )

    if (response.data.location) {
      store.setMylocation({
        isAccurate: false,
        latlng: response.data.location,
      })

      const lat = response.data.location.lat
      const lng = response.data.location.lng
      const response2 = await axios.post(
        `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat}` +
          `,${lng}&result_type=country` +
          `&key=` +
          config.public.googleMapsKey
      )

      store.countryCode =
        response2.data.results[0].address_components[0].short_name
    }
  } catch (e) {
    console.error('Geolocation failed:', e)
  }

  if (typeof localStorage !== 'undefined') {
    if (
      !useDevice().isMobile() &&
      !localStorage.getItem('welcomeBoxHidden')
    ) {
      welcomeboxShown.value = true
    }
  }

  window.setTimeout(() => (store.justMounted = false), 5000)
})

function locationPicked() {
  if (filterboxRef.value) {
    filterboxRef.value.collapse()
  }
}

function doShowLogin() {
  loginboxShown.value = true
}

function doHideLogin() {
  loginboxShown.value = false
}

function hideWelcomeBox() {
  welcomeboxShown.value = false
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('welcomeBoxHidden', true)
  }
}
</script>

<style lang="scss">
body {
  position: fixed;
}

::-webkit-scrollbar {
  -webkit-appearance: none;
  width: 7px;
}

::-webkit-scrollbar-thumb {
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.5);
  -webkit-box-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
}

a {
  @apply text-blue-600;
}

a:hover {
  @apply underline;
}

.submit-ribbon {
  position: fixed;
  bottom: 0;
  left: 0;
  z-index: 100;
  overflow: hidden;
  width: 150px;
  height: 150px;
  cursor: pointer;

  span {
    position: absolute;
    display: block;
    width: 225px;
    padding: 10px 0;
    background-color: #dc2626;
    color: white;
    font-weight: 600;
    font-size: 13px;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
    transform: rotate(45deg);
    bottom: 30px;
    left: -55px;
    transition: background-color 0.2s;
  }

  &:hover span {
    background-color: #b91c1c;
  }
}
</style>
