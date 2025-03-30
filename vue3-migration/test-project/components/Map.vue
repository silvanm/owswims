<template>
  <div>
    <!-- Containers which will be included in Google Maps. Hiding them by default -->
    <div class="hidden">
      <div ref="sponsor">
        <transition name="fade">
          <div
            v-if="!isMobile || justMounted"
            style="
              background-color: white;
              border-radius: 2px;
              margin: 24px;
              padding: 9px;
            "
          >
            {{ t('poweredBy') }}
            <a href="https://muehlemann-popp.ch">
              <span style="font-weight: bold; margin-top: 5px; display: inline-block;">
                Mühlemann & Popp
              </span>
            </a>
          </div>
        </transition>
      </div>
      <div
        ref="centerButton"
        :title="t('tooltipCenterButton')"
        class="map-button"
      >
        <button class="text-gray-600" @click="centerMap">
          <font-awesome-icon
            icon="location-arrow"
            size="2x"
          ></font-awesome-icon>
        </button>
      </div>
      <div
        ref="seeAllButton"
        :title="t('tooltipSeeAll')"
        class="map-button"
        style="padding: 9px 9px 9px 11px"
      >
        <button class="text-gray-600" @click="seeAll">
          <font-awesome-icon
            icon="expand-arrows-alt"
            size="2x"
          ></font-awesome-icon>
        </button>
      </div>

      <div ref="eventDescription">
        <div v-if="pickedLocation && pickedLocationData">
          <h1 class="text-xl font-semibold">
            {{ pickedLocation.city }}, {{ pickedLocation.country }}
          </h1>
          <span v-if="mylocation.isAccurate">
            {{ t('travelTime') }}:
            {{ formattedTravelDistance }}
          </span>
          <div
            v-for="event in pickedLocationData.allEvents.edges"
            :key="event.node.id"
          >
            <div style="margin-top: 10px">
              {{ formatEventDate(event.node.dateStart) }}<br />
              <a
                :href="event.node.website"
                target="_blank"
                class="font-semibold"
                >{{ event.node.name }}
                <font-awesome-icon
                  icon="external-link-square-alt"
                ></font-awesome-icon> </a
              ><br />
              {{ formatRaceDistances(event.node.races) }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <div id="map"></div>
    <CourseEditor
      v-if="raceTrackUnderEditId"
      :map="map"
    ></CourseEditor>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useMainStore } from '../stores/main'
// Import the useI18n composable directly
import { useI18n } from '../composables/useI18n.js'
import { useEventPresentation } from '../composables/useEventPresentation'
import { useCalculateDistance } from '../composables/useCalculateDistance'
import { useRoute } from 'vue-router'
import { useDeviceDetector } from '../composables/useDeviceDetector'
import { useToast } from '../composables/useToast'
import { useUrlHistory } from '../composables/useUrlHistory'
import { useQueries } from '../composables/useQueries'
import _ from 'lodash'

export default {
  name: 'MapComponent',
  props: {
    locations: {
      type: Array,
      default: () => {
        return []
      },
    },
    distanceFrom: {
      type: Number,
      default: () => {
        return 0
      },
    },
    distanceTo: {
      type: Number,
      default: () => {
        return 100
      },
    },
    dateRange: {
      type: Array,
      default: () => {
        return [-10, 10]
      },
    },
  },
  emits: ['locationPicked'],
  setup(props, { emit }) {
    // Stores and composables
    const mainStore = useMainStore()
    // Get the translation function from i18n
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { t } = useI18n()
    // const router = useRouter() - Not used
    const route = useRoute()
    const { isMobile } = useDeviceDetector()
    const toast = useToast()
    const urlHistory = useUrlHistory()
    const queries = useQueries()
    const { 
      formatEventDate, 
      humanizeDistance, 
      getFormattedTravelDistance 
    } = useEventPresentation()
    const { calculateDistance } = useCalculateDistance()

    // Refs
    const sponsor = ref(null)
    const centerButton = ref(null)
    const seeAllButton = ref(null)
    const eventDescription = ref(null)
    const marker = ref({})
    const markerFocused = ref(null)
    const locationIdToMarker = ref({})
    const pickedLocationId = ref('TG9jYXRpb25Ob2RlOjE4NTg=')
    const pickedLocation = ref(null)
    const formattedTravelDistance = ref('')
    const google = ref({})
    const map = ref({})
    const raceTrackOverlays = ref({})
    const myLocationMarker = ref(null)

    // Computed properties
    const mylocation = computed(() => mainStore.mylocation)
    const pickedLocationData = computed(() => mainStore.pickedLocationData)
    const pickedLocationZoomedIn = computed(() => mainStore.pickedLocationZoomedIn)
    const organizerData = computed(() => mainStore.organizerData)
    const isLoading = computed(() => mainStore.isLoading)
    const raceTrackUnderEditId = computed(() => mainStore.raceTrackUnderEditId)
    const raceTrackUnderFocusId = computed(() => mainStore.raceTrackUnderFocusId)
    const raceTrackUnderHoverId = computed(() => mainStore.raceTrackUnderHoverId)
    const raceTrackDeletedId = computed(() => mainStore.raceTrackDeletedId)
    const justMounted = computed(() => mainStore.justMounted)

    // Methods
    function formatRaceDistances(races) {
      function onlyUnique(value, index, self) {
        return self.indexOf(value) === index
      }

      const raceDistances = races.edges.map((e) => {
        return e.node.distance
      })

      return raceDistances
        .sort((a, b) => {
          return a > b ? 1 : -1
        })
        .map((e) => humanizeDistance(e))
        .filter(onlyUnique)
        .join(', ')
    }

    function updateMarker() {
      const infowindow = new google.value.maps.InfoWindow({
        content: eventDescription.value,
        fontFamily: "'Source Sans Pro', sans-serif",
        pixelOffset: new google.value.maps.Size(-54 / 2, 0),
      })

      if (window.markerCluster) {
        window.markerCluster.clearMarkers()
      }

      for (const id of Object.keys(marker.value)) {
        marker.value[id].setMap(null)
        // Instead of deleting, set to null to avoid ESLint error
        marker.value[id] = null
      }

      for (const location of props.locations) {
        if (!(location.lat && location.lng)) {
          // latLng is mandatory
          continue
        }

        const ratingForMarker = location.averageRating
          ? Math.round(location.averageRating)
          : 0

        const markerObj = new google.value.maps.Marker({
          icon: markerPin(ratingForMarker),
          position: location,
          map: map.value,
          title: location.name,
          shape: { coords: [0, 0, 28, 70 / 2], type: 'rect' },
        })

        locationIdToMarker.value[location.id] = markerObj

        markerObj.addListener('click', () => {
          mainStore.$patch({ pickedLocationId: location.id })
          emit('locationPicked')
          // TODO: Add gtag event
          pickedLocationId.value = location.id
          pickedLocation.value = location
          const locationVal = location
          const markerObjVal = markerObj
          infowindow.close()
          calculateDistance(google.value, locationVal, () => {
            formattedTravelDistance.value = getFormattedTravelDistance(locationVal)
            infowindow.open(map.value, markerObjVal)
          })
        })

        marker.value[location.id] = markerObj
      }

      // Initialize MarkerClusterer
      if (window.MarkerClusterer) {
        window.markerCluster = new window.MarkerClusterer(map.value, Object.values(marker.value), {
          styles: [
            {
              width: 30,
              height: 30,
              className: 'custom-clustericon-1',
            },
            {
              width: 40,
              height: 40,
              className: 'custom-clustericon-2',
            },
            {
              width: 50,
              height: 50,
              className: 'custom-clustericon-3',
            },
          ],
          clusterClass: 'custom-clustericon',
          gridSize: 30,
        })
      }
    }

    function countVisibleMarkers() {
      const bounds = map.value.getBounds()
      let count = 0

      Object.keys(marker.value).forEach((k) => {
        const markerItem = marker.value[k]
        if (bounds.contains(markerItem.getPosition()) === true) {
          count++
        }
      })
      return count
    }

    function seeAll() {
      /* Expand map to see all markers */
      const bounds = new window.google.maps.LatLngBounds()
      props.locations.forEach(function (item) {
        bounds.extend(new window.google.maps.LatLng(item.lat, item.lng))
      })
      map.value.fitBounds(bounds, {
        top: window.innerHeight / 10,
        left: window.innerWidth / 10,
        bottom: window.innerHeight / 10,
        right: window.innerWidth / 10,
      })
    }

    async function centerMap() {
      await mainStore.locateMe()

      if (mylocation.value.latlng.lat && mylocation.value.latlng.lng) {
        const myLatLng = new google.value.maps.LatLng(
          mylocation.value.latlng.lat,
          mylocation.value.latlng.lng
        )
        map.value.panTo(myLatLng)
      }
    }

    function markerPin(rating = 0) {
      // Use a simple circle with a label for testing
      // Adjust color based on rating
      const colors = ['#CCCCCC', '#4299E1', '#38B2AC', '#48BB78', '#ECC94B', '#ED8936']
      const color = colors[Math.min(rating, colors.length - 1)]
      
      return {
        path: google.value.maps.SymbolPath.CIRCLE,
        fillColor: color,
        fillOpacity: 1,
        scale: 10,
        strokeWeight: 2,
        strokeColor: '#FFFFFF',
        labelOrigin: new google.value.maps.Point(0, 0),
      }
    }

    function openLocation(id) {
      google.value.maps.event.trigger(locationIdToMarker.value[id], 'click')
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
      // hide labels if zoomed out
      for (const raceId of Object.keys(raceTrackOverlays.value)) {
        raceTrackOverlays.value[raceId].label.setVisible(isLabelVisible())
      }
      const query = { zoom: map.value.getZoom() }
      urlHistory.push(query, null)
    }

    function drawRaceTrackOverlays(location) {
      // Draw Race Track Overlays
      location.allEvents.edges.forEach((event) => {
        event.node.races.edges.forEach((race) => {
          if (
            race.node.coordinates &&
            race.node.coordinates.length > 0 &&
            !(race.node.id in raceTrackOverlays.value)
          ) {
            const coordinateObj = race.node.coordinates

            const coords = coordinateObj.map((i) => {
              return {
                lat: i[0],
                lng: i[1],
              }
            })

            const arrowSymbol = {
              path: google.value.maps.SymbolPath.FORWARD_CLOSED_ARROW,
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

            const raceTrackOverlay = new google.value.maps.Polyline(polylineOptions)

            // take the middle coordinate and apply a label there
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
              icon:
                'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
              label: {
                className: 'marker-passive ' + positionClass,
                color: 'white',
                text: humanizeDistance(race.node.distance),
                fontSize: '12px',
              },
              visible: isLabelVisible(),
            }

            // add a marker without icon to achieve a label
            const label = new google.value.maps.Marker(labelOptions)

            raceTrackOverlay.setMap(map.value)
            raceTrackOverlays.value[race.node.id] = {
              polyline: raceTrackOverlay,
              // did not find out how I can retrieve the options from an existing polyline
              // so I can modify them. That's why I am storing the option object
              polylineOptions,
              labelOptions,
              label,
            }
          }
        })
      })
    }

    function drawRaceTrackOverlaysForEachVisibleLocation() {
      // triggers the loading of each location detail.
      props.locations.forEach((location) => {
        const c = queries.location(
          location.id,
          mainStore.keyword,
          mainStore.dateRange
        )
        c.then((l) => drawRaceTrackOverlays(l.data))
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

    // Watchers
    watch(() => props.locations, (newlocations) => {
      updateMarker()
      if (countVisibleMarkers() === 0 && newlocations.length > 0) {
        seeAll()
      }
      if (newlocations.length === 0) {
        toast.error('No races found. Deactivate some of the filters.')
      }
    })

    watch(mylocation, (newLocation) => {
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
          anchor: new google.value.maps.Point(0, 0),
          strokeWeight: 1,
          strokeColor: '#fff',
          scale: 0.25,
        }
        myLocationMarker.value = new google.value.maps.Marker({
          icon,
          position: newLocation.latlng,
          map: map.value,
        })
      }
    })

    watch(pickedLocationData, (newData) => {
      drawRaceTrackOverlays(newData)
    })

    watch(pickedLocationZoomedIn, (newData) => {
      openLocation(newData)
      map.value.panTo(locationIdToMarker.value[newData].position)
      map.value.setZoom(12)
    })

    watch(raceTrackUnderEditId, (newData) => {
      for (const raceId of Object.keys(raceTrackOverlays.value)) {
        const color = newData === raceId ? '#FFFF00' : '#FFFFFF'
        raceTrackOverlays.value[raceId].polyline.setOptions({
          strokeColor: color,
        })
      }
    })

    watch(raceTrackUnderHoverId, (newData) => {
      // Called when one hovers over a racetrack
      highlightRacetrack(newData)
    })

    watch(raceTrackUnderFocusId, (newData) => {
      // Called when one *clicks* on a racetrack
      highlightRacetrack(newData)

      if (newData && raceTrackOverlays.value[newData]) {
        // get bounds of racetrack
        google.value.maps.Polyline.prototype.getBounds = function () {
          const bounds = new google.value.maps.LatLngBounds()
          this.getPath().forEach(function (item, _index) {
            bounds.extend(new google.value.maps.LatLng(item.lat(), item.lng()))
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
    })

    watch(raceTrackDeletedId, (newData) => {
      raceTrackOverlays.value[newData].label.setMap(null)
      raceTrackOverlays.value[newData].polyline.setMap(null)
    })

    // Lifecycle hooks
    onMounted(() => {
      // Initialize Google Maps
      if (!window.google || !window.google.maps) {
        console.error('Google Maps API not loaded')
        return
      }

      google.value = window.google

      let center
      if (
        route.query.lat &&
        route.query.lng
      ) {
        center = mylocation.value.latlng = {
          lat: parseFloat(route.query.lat),
          lng: parseFloat(route.query.lng),
        }
      } else if (mylocation.value.latlng.lat && mylocation.value.latlng.lng) {
        center = mylocation.value.latlng
      } else {
        // fallback to switzerland
        center = { lat: 47.3474476, lng: 8.6733976 }
      }
      map.value = new google.value.maps.Map(document.getElementById('map'), {
        center,
        zoom: route.query.zoom
          ? parseInt(route.query.zoom)
          : 5,
        disableDefaultUI: false,
        mapTypeId: mainStore.mapType
          ? mainStore.mapType
          : google.value.maps.MapTypeId.HYBRID,
        gestureHandling: 'greedy',
        mapTypeControlOptions: {
          style: google.value.maps.MapTypeControlStyle.HORIZONTAL_BAR,
          position: google.value.maps.ControlPosition.TOP_RIGHT,
        },
      })
      map.value.controls[google.value.maps.ControlPosition.RIGHT].push(
        centerButton.value
      )
      map.value.controls[google.value.maps.ControlPosition.RIGHT].push(
        seeAllButton.value
      )
      map.value.controls[google.value.maps.ControlPosition.BOTTOM_CENTER].push(
        sponsor.value
      )
      updateMarker()
      if (route.query.location) {
        openLocation(route.query.location)
      }

      map.value.addListener('zoom_changed', () => {
        zoomChanged()
      })

      map.value.addListener('center_changed', () => {
        centerChangedDebounced()
      })

      // this is set by the query string "event"
      const zoomedInLocation = pickedLocationZoomedIn.value
      if (zoomedInLocation) {
        // This makes sure that the map is not recentered or rezoomed on every
        // click of a location
        if (!route.query.zoom) {
          map.value.panTo(locationIdToMarker.value[zoomedInLocation].position)
          map.value.setZoom(12)
        }
        openLocation(zoomedInLocation)
      }

      // filter by organization --> pan so that all markers are seen
      if (organizerData.value) {
        drawRaceTrackOverlaysForEachVisibleLocation()
        if (!route.query.zoom) {
          seeAll()
        }
      }
    })

    // Debounced functions
    const centerChangedDebounced = _.debounce(centerChanged, 2000)

    return {
      // Refs
      sponsor,
      centerButton,
      seeAllButton,
      eventDescription,
      marker,
      markerFocused,
      locationIdToMarker,
      pickedLocationId,
      pickedLocation,
      formattedTravelDistance,
      google,
      map,
      raceTrackOverlays,
      myLocationMarker,

      // Computed
      mylocation,
      pickedLocationData,
      pickedLocationZoomedIn,
      organizerData,
      isLoading,
      raceTrackUnderEditId,
      raceTrackUnderFocusId,
      raceTrackUnderHoverId,
      raceTrackDeletedId,
      justMounted,
      isMobile,

      // Methods
      formatRaceDistances,
      updateMarker,
      countVisibleMarkers,
      seeAll,
      centerMap,
      markerPin,
      formatEventDate,
      openLocation,
      centerChanged,
      zoomChanged,
      drawRaceTrackOverlays,
      drawRaceTrackOverlaysForEachVisibleLocation,
      isLabelVisible,
      highlightRacetrack,

      // i18n
      t,
    }
  }
}
</script>

<style>
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
  padding: 9px;

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

.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
