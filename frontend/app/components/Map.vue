<template>
  <div>
    <!-- Containers which will be included in Google Maps. Hiding them by default -->
    <div class="hidden">
      <div ref="sponsorEl">
        <Transition name="fade">
          <div
            v-if="!useDevice().isMobile() || store.justMounted"
            style="
              background-color: white;
              border-radius: 2px;
              margin: 24px;
              padding: 9px;
            "
          >
            {{ t('poweredBy') }}
            <a href="https://muehlemann-popp.ch">
              <img
                src="~/assets/Mühlemann&Popp.svg"
                style="width: 120px; margin-top: 5px"
              />
            </a>
          </div>
        </Transition>
      </div>
      <div
        ref="centerButtonEl"
        v-tooltip="{
          content: t('tooltipCenterButton'),
          trigger: 'hover',
          placement: 'left',
        }"
        class="map-button"
      >
        <button class="text-gray-600" @click="centerMap">
          <FontAwesomeIcon icon="location-arrow" size="2x" />
        </button>
      </div>
      <div
        ref="seeAllButtonEl"
        v-tooltip="{
          content: t('tooltipSeeAll'),
          trigger: 'hover',
          placement: 'left',
        }"
        class="map-button"
        style=""
      >
        <button class="text-gray-600" @click="seeAll">
          <FontAwesomeIcon icon="expand-arrows-alt" size="2x" />
        </button>
      </div>

      <div ref="eventDescriptionEl">
        <div v-if="pickedLocation && store.pickedLocationData">
          <h1 class="text-xl font-semibold">
            {{ pickedLocation.city }}, {{ pickedLocation.country }}
          </h1>
          <span v-if="store.mylocation.isAccurate">
            {{ t('travelTime') }}:
            {{ formattedTravelDistance }}
          </span>
          <div
            v-for="event in store.pickedLocationData.allEvents.edges"
            :key="event.node.id"
          >
            <div style="margin-top: 10px">
              {{ formatEventDate(event.node.dateStart) }}<br />
              <a
                :href="event.node.website"
                target="_blank"
                class="font-semibold"
                >{{ event.node.name }}
                <FontAwesomeIcon icon="external-link-square-alt" />
              </a><br />
              {{ formatRaceDistances(event.node.races) }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <div id="map"></div>
    <CourseEditor
      v-if="store.raceTrackUnderEditId"
      :map="map"
    />
  </div>
</template>

<script setup>
import { ref, shallowRef, watch, onMounted, markRaw } from 'vue'
import gql from 'graphql-tag'
import { MarkerClusterer } from '@googlemaps/markerclusterer'
import { debounce } from 'lodash-es'
import { formatISO } from 'date-fns'

const props = defineProps({
  locations: {
    type: Array,
    default: () => [],
  },
  distanceFrom: {
    type: Number,
    default: 0,
  },
  distanceTo: {
    type: Number,
    default: 100,
  },
  dateRange: {
    type: Array,
    default: () => [-10, 10],
  },
})

const emit = defineEmits(['locationPicked'])

const { t } = useI18n()
const store = useMainStore()
const route = useRoute()
const config = useRuntimeConfig()
const { gtag } = useGtag()
const { $apollo } = useNuxtApp()
const urlHistory = useUrlHistory()

const {
  formatEventDate,
  humanizeDistance,
  getFormattedTravelDistance,
} = useEventPresentation()

// Template refs
const sponsorEl = ref(null)
const centerButtonEl = ref(null)
const seeAllButtonEl = ref(null)
const eventDescriptionEl = ref(null)

// Data
const marker = ref({})
const markerFocused = ref(null)
const locationIdToMarker = ref({})
const pickedLocationIdLocal = ref('TG9jYXRpb25Ob2RlOjE4NTg=')
const pickedLocation = ref(null)
const travelTimes = ref({})
const formattedTravelDistance = ref('')
const map = shallowRef(null)
const raceTrackOverlays = ref({})
let markerCluster = null
let myLocationMarker = null

// Watchers
watch(
  () => props.locations,
  (newlocations) => {
    updateMarker()
    if (countVisibleMarkers() === 0 && newlocations.length > 0) {
      seeAll()
    }
    if (newlocations.length === 0) {
      console.log('No races found. Deactivate some of the filters.')
    }
  }
)

watch(
  () => store.mylocation,
  (newLocation) => {
    if (
      newLocation.latlng.lat &&
      newLocation.latlng.lng &&
      newLocation.isAccurate
    ) {
      const icon = {
        path:
          'M 25, 50\n' +
          '    a 25,25 0 1,1 50,0\n' +
          '    a 25,25 0 1,1 -50,0',
        fillColor: '#4299E1',
        fillOpacity: 1,
        anchor: new google.maps.Point(0, 0),
        strokeWeight: 1,
        strokeColor: '#fff',
        scale: 0.25,
      }
      myLocationMarker = markRaw(new google.maps.Marker({
        icon,
        position: newLocation.latlng,
        map: map.value,
      }))
    }
  }
)

watch(
  () => store.pickedLocationData,
  (newData) => {
    if (newData) {
      drawRaceTrackOverlays(newData)
    }
  }
)

watch(
  () => store.pickedLocationZoomedIn,
  (newData) => {
    if (newData) {
      openLocation(newData)
      if (locationIdToMarker.value[newData]) {
        map.value.panTo(locationIdToMarker.value[newData].position)
        map.value.setZoom(12)
      }
    }
  }
)

watch(
  () => store.raceTrackUnderEditId,
  (newData) => {
    for (const raceId of Object.keys(raceTrackOverlays.value)) {
      const color = newData === raceId ? '#FFFF00' : '#FFFFFF'
      raceTrackOverlays.value[raceId].polyline.setOptions({
        strokeColor: color,
      })
    }
  }
)

watch(
  () => store.raceTrackUnderHoverId,
  (newData) => {
    highlightRacetrack(newData)
  }
)

watch(
  () => store.raceTrackUnderFocusId,
  (newData) => {
    highlightRacetrack(newData)

    if (newData && raceTrackOverlays.value[newData]) {
      google.maps.Polyline.prototype.getBounds = function () {
        const bounds = new google.maps.LatLngBounds()
        this.getPath().forEach(function (item) {
          bounds.extend(new google.maps.LatLng(item.lat(), item.lng()))
        })
        return bounds
      }
      map.value.fitBounds(
        raceTrackOverlays.value[newData].polyline.getBounds(),
        {
          top: window.innerHeight / 10,
          left: window.innerWidth / 10,
          bottom: window.innerHeight / 10,
          right: window.innerWidth / 10,
        }
      )
    }
  }
)

watch(
  () => store.raceTrackDeletedId,
  (newData) => {
    if (newData && raceTrackOverlays.value[newData]) {
      raceTrackOverlays.value[newData].label.setMap(null)
      raceTrackOverlays.value[newData].polyline.setMap(null)
    }
  }
)

onMounted(() => {
  initMap()
})

// Methods
async function initMap() {
  if (typeof window !== 'undefined' && !window.googleMapsReady) {
    try {
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(
          () => reject(new Error('Google Maps load timeout')),
          10000
        )
        window.addEventListener(
          'google-maps-ready',
          () => {
            clearTimeout(timeout)
            resolve()
          },
          { once: true }
        )
      })
    } catch (err) {
      console.error('Failed to load Google Maps:', err)
      return
    }
  }

  let center
  if (route.query.lat && route.query.lng) {
    store.setMylocation({
      isAccurate: false,
      latlng: {
        lat: parseFloat(route.query.lat),
        lng: parseFloat(route.query.lng),
      },
    })
    center = {
      lat: parseFloat(route.query.lat),
      lng: parseFloat(route.query.lng),
    }
  } else if (store.mylocation.latlng.lat && store.mylocation.latlng.lng) {
    center = store.mylocation.latlng
  } else {
    center = { lat: 47.3474476, lng: 8.6733976 }
  }

  map.value = markRaw(new google.maps.Map(document.getElementById('map'), {
    center,
    zoom: route.query.zoom ? parseInt(route.query.zoom) : 5,
    disableDefaultUI: false,
    mapTypeId: store.mapType
      ? store.mapType
      : google.maps.MapTypeId.HYBRID,
    gestureHandling: 'greedy',
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
      position: google.maps.ControlPosition.TOP_RIGHT,
    },
  }))

  map.value.controls[google.maps.ControlPosition.RIGHT].push(
    centerButtonEl.value
  )
  map.value.controls[google.maps.ControlPosition.RIGHT].push(
    seeAllButtonEl.value
  )
  map.value.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(
    sponsorEl.value
  )

  updateMarker()

  if (route.query.location) {
    openLocation(route.query.location)
  }

  map.value.addListener('zoom_changed', () => {
    zoomChanged()
  })

  const debouncedCenterChanged = debounce(centerChanged, 2000)
  map.value.addListener('center_changed', () => {
    debouncedCenterChanged()
  })

  const zoomedInLocation = store.pickedLocationZoomedIn
  if (zoomedInLocation) {
    if (!route.query.zoom) {
      if (locationIdToMarker.value[zoomedInLocation]) {
        map.value.panTo(locationIdToMarker.value[zoomedInLocation].position)
        map.value.setZoom(12)
      }
    }
    openLocation(zoomedInLocation)
  }

  if (store.organizerData) {
    drawRaceTrackOverlaysForEachVisibleLocation()
    if (!route.query.zoom) {
      seeAll()
    }
  }
}

function countVisibleMarkers() {
  if (!map.value || !map.value.getBounds) return 0
  const bounds = map.value.getBounds()
  if (!bounds) return 0
  let count = 0
  Object.keys(marker.value).forEach((k) => {
    const m = marker.value[k]
    if (bounds.contains(m.getPosition()) === true) {
      count++
    }
  })
  return count
}

function seeAll() {
  const bounds = new google.maps.LatLngBounds()
  props.locations.forEach((item) => {
    bounds.extend(new google.maps.LatLng(item.lat, item.lng))
  })
  map.value.fitBounds(bounds, {
    top: window.innerHeight / 10,
    left: window.innerWidth / 10,
    bottom: window.innerHeight / 10,
    right: window.innerWidth / 10,
  })
}

async function centerMap() {
  await store.locateMe()
  if (store.mylocation.latlng.lat && store.mylocation.latlng.lng) {
    const myLatLng = new google.maps.LatLng(
      store.mylocation.latlng.lat,
      store.mylocation.latlng.lng
    )
    map.value.panTo(myLatLng)
  }
}

function markerPin(rating = 0) {
  // In Nuxt 4, dynamic asset imports need a different approach
  // Using a URL constructor for the marker images
  return {
    url: `/markers/Marker${rating}.png`,
    scaledSize: new google.maps.Size(168 / 2, 92 / 2),
    anchor: new google.maps.Point(28 / 2, 70 / 2),
  }
}

function formatRaceDistances(races) {
  function onlyUnique(value, index, self) {
    return self.indexOf(value) === index
  }

  const raceDistances = races.edges.map((e) => e.node.distance)

  return raceDistances
    .sort((a, b) => (a > b ? 1 : -1))
    .map((e) => humanizeDistance(e))
    .filter(onlyUnique)
    .join(', ')
}

function updateMarker() {
  if (!map.value) return

  const infowindow = new google.maps.InfoWindow({
    content: eventDescriptionEl.value,
    fontFamily: "'Source Sans Pro', sans-serif",
    pixelOffset: new google.maps.Size(-54 / 2, 0),
  })

  if (markerCluster) {
    markerCluster.setMap(null)
    markerCluster = null
  }

  for (const id of Object.keys(marker.value)) {
    marker.value[id].setMap(null)
    delete marker.value[id]
  }

  for (const location of props.locations) {
    if (!(location.lat && location.lng)) {
      continue
    }

    const ratingForMarker = location.averageRating
      ? Math.round(location.averageRating)
      : 0

    const markerObj = markRaw(new google.maps.Marker({
      icon: markerPin(ratingForMarker),
      position: location,
      title: location.name,
      shape: { coords: [0, 0, 28, 70 / 2], type: 'rect' },
    }))

    locationIdToMarker.value[location.id] = markerObj

    markerObj.addListener('click', async () => {
      store.pickedLocationId = location.id
      emit('locationPicked')
      gtag('event', 'locationPicked', location.id)
      pickedLocationIdLocal.value = location.id
      pickedLocation.value = location
      infowindow.close()
      await store.fetchPickedLocationData(location.id)
      calculateDistance(location, () => {
        formattedTravelDistance.value = getFormattedTravelDistance(
          location,
          'DRIVING'
        )
        infowindow.open(map.value, markerObj)
      })
    })

    marker.value[location.id] = markerObj
  }

  markerCluster = new MarkerClusterer({
    map: map.value,
    markers: Object.values(marker.value),
    renderer: {
      render({ count, position }) {
        const size = Math.min(30 + Math.floor(count / 5) * 2, 50)
        const svg = window.btoa(`
          <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
            <circle cx="${size / 2}" cy="${size / 2}" r="${size / 2}" fill="#006eba" opacity="0.3"/>
            <circle cx="${size / 2}" cy="${size / 2}" r="${size / 2 - 4}" fill="#006eba" opacity="0.5"/>
            <circle cx="${size / 2}" cy="${size / 2}" r="${size / 2 - 8}" fill="#006eba"/>
          </svg>
        `)
        return new google.maps.Marker({
          position,
          icon: {
            url: `data:image/svg+xml;base64,${svg}`,
            scaledSize: new google.maps.Size(size, size),
            anchor: new google.maps.Point(size / 2, size / 2),
          },
          label: {
            text: String(count),
            color: 'white',
            fontSize: '12px',
            fontWeight: 'bold',
          },
          zIndex: Number(google.maps.Marker.MAX_ZINDEX) + count,
        })
      },
    },
  })
}

function calculateDistance(location, callback) {
  const requestedDestinations = []
  const k = `${location.lat},${location.lng}`
  if (!(k in store.travelTimes)) {
    requestedDestinations.push(k)
  }

  if (requestedDestinations.length === 0) {
    callback()
    return
  }

  if (!store.mylocation.isAccurate) {
    callback()
    return
  }

  const service = new google.maps.DistanceMatrixService()
  const travelModes = [google.maps.TravelMode.DRIVING]

  const promises = travelModes.map((travelMode) => {
    return service.getDistanceMatrix({
      origins: [store.mylocation.latlng],
      destinations: [k],
      transitOptions: {
        departureTime: new Date(2020, 8, 2, 8, 0, 0),
      },
      travelMode,
      unitSystem: google.maps.UnitSystem.METRIC,
    })
  })

  Promise.all(promises).then((values) => {
    const updatedTravelTimes = { ...store.travelTimes }
    values.forEach((value, ix) => {
      const results = value.rows[0].elements
      for (let j = 0; j < results.length; j++) {
        if (!updatedTravelTimes[requestedDestinations[j]]) {
          updatedTravelTimes[requestedDestinations[j]] = {
            DRIVING: null,
            TRANSIT: null,
          }
        }
        if (results[j].status === 'OK') {
          updatedTravelTimes[requestedDestinations[j]] = {
            distance: results[j].distance.value,
            duration: results[j].duration.value,
          }
        } else {
          updatedTravelTimes[requestedDestinations[j]][travelModes[ix]] = null
        }
      }
    })
    store.travelTimes = updatedTravelTimes
    callback()
  })
}

function openLocation(id) {
  if (locationIdToMarker.value[id]) {
    google.maps.event.trigger(locationIdToMarker.value[id], 'click')
  }
}

function centerChanged() {
  if (map.value) {
    const query = {}
    query.lat = map.value.getCenter().lat()
    query.lng = map.value.getCenter().lng()
    urlHistory.push(query, null)
  }
}

function zoomChanged() {
  for (const raceId of Object.keys(raceTrackOverlays.value)) {
    raceTrackOverlays.value[raceId].label.setVisible(isLabelVisible())
  }
  const query = { zoom: map.value.getZoom() }
  urlHistory.push(query, null)
}

function drawRaceTrackOverlays(locationData) {
  locationData.allEvents.edges.forEach((event) => {
    event.node.races.edges.forEach((race) => {
      if (
        race.node.coordinates &&
        race.node.coordinates.length > 0 &&
        !(race.node.id in raceTrackOverlays.value)
      ) {
        const coordinateObj = race.node.coordinates

        const coords = coordinateObj.map((i) => ({
          lat: i[0],
          lng: i[1],
        }))

        const arrowSymbol = {
          path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
          fillColor: 'white',
          fillOpacity: 0,
          strokeOpacity: 0,
        }

        const icons = []
        const numArrows = coords.length
        for (let i = 0; i < numArrows; i++) {
          icons.push({
            icon: arrowSymbol,
            offset: ((100 / numArrows) * i).toString() + '%',
          })
        }

        const polylineOptions = {
          path: coords,
          geodesic: true,
          strokeColor: '#FFFFFF',
          strokeOpacity: 0.5,
          strokeWeight: 3,
          icons,
        }

        const raceTrackOverlay = new google.maps.Polyline(polylineOptions)

        const coordIx = Math.floor(coords.length / 2) - 1
        const middleCoordinate = {
          lat: (coords[coordIx].lat + coords[coordIx + 1].lat) / 2,
          lng: (coords[coordIx].lng + coords[coordIx + 1].lng) / 2,
        }

        const slope =
          (coords[coordIx + 1].lat - coords[coordIx].lat) /
          (coords[coordIx + 1].lng - coords[coordIx].lng)

        let positionClass = 'marker-east'
        if (Math.abs(slope) < 1) {
          positionClass = 'marker-south'
        }

        const labelOptions = {
          positionClass,
          position: middleCoordinate,
          map: map.value,
          icon: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
          label: {
            className: 'marker-passive ' + positionClass,
            color: 'white',
            text: humanizeDistance(race.node.distance),
            fontSize: '12px',
          },
          visible: isLabelVisible(),
        }

        const label = new google.maps.Marker(labelOptions)

        raceTrackOverlay.setMap(map.value)
        raceTrackOverlays.value[race.node.id] = {
          polyline: raceTrackOverlay,
          polylineOptions,
          labelOptions,
          label,
        }
      }
    })
  })
}

function drawRaceTrackOverlaysForEachVisibleLocation() {
  props.locations.forEach((location) => {
    $apollo
      .query({
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
          locationId: location.id,
          keyword: store.keyword,
          dateFrom: formatISO(store.dateRange[0], {
            representation: 'date',
          }),
          dateTo: formatISO(store.dateRange[1], {
            representation: 'date',
          }),
        },
      })
      .then((result) => drawRaceTrackOverlays(result.data))
  })
}

function isLabelVisible() {
  const zoom = map.value.getZoom()
  return zoom > 9
}

function highlightRacetrack(id) {
  for (const raceId of Object.keys(raceTrackOverlays.value)) {
    const po = raceTrackOverlays.value[raceId].polylineOptions
    const lo = raceTrackOverlays.value[raceId].labelOptions
    if (id === raceId) {
      po.strokeOpacity = 1
      po.icons.forEach((i) => (i.icon.fillOpacity = 1))
      lo.label.className = 'marker-active ' + lo.positionClass
    } else {
      po.strokeOpacity = 0.5
      po.icons.forEach((i) => (i.icon.fillOpacity = 0))
      lo.label.className = 'marker-passive ' + lo.positionClass
    }
    raceTrackOverlays.value[raceId].polyline.setOptions(po)
    raceTrackOverlays.value[raceId].label.setOptions(lo)
  }
}
</script>

<style lang="scss">
html,
body {
  height: 100%;
  width: 100%;
}

#map {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.map-button {
  background-color: white;
  border-radius: 2px;
  margin: 10px;
  height: 40px;
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;

  button:focus {
    outline: none;
  }
}

.marker-active {
  position: relative;
  opacity: 1;
}

.marker-passive {
  position: relative;
  opacity: 0.5;
}

.marker-east {
  left: 20px;
}

.marker-south {
  top: 20px;
}

.gm-style .gm-style-iw {
  font-family: 'Source Sans Pro', sans-serif;
}

.gm-style .gm-style-iw-c {
  border-radius: 0;
}

.gm-style a {
  color: #4299e1;
}

.custom-clustericon {
  background: var(--cluster-color);
  color: #fff;
  border-radius: 100%;
  font-weight: bold;
  font-size: 15px;
  display: flex;
  align-items: center;
}

.custom-clustericon::before,
.custom-clustericon::after {
  content: '';
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;

  transform: translate(-50%, -50%);
  top: 50%;
  left: 50%;
  background: var(--cluster-color);
  opacity: 0.2;
  border-radius: 100%;
}

.custom-clustericon::before {
  padding: 7px;
}

.custom-clustericon::after {
  padding: 14px;
}

.custom-clustericon-1,
.custom-clustericon-2,
.custom-clustericon-3 {
  --cluster-color: #4299e1;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
