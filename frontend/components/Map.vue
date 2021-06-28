<template>
  <div>
    <!-- Containers which will be included in Google Maps. Hiding them by default -->
    <div class="hidden">
      <div ref="sponsor">
        <transition name="fade">
          <div
            v-if="!$device.isMobile() || $store.getters.justMounted"
            style="
              background-color: white;
              border-radius: 2px;
              margin: 24px;
              padding: 9px;
            "
          >
            {{ $t('poweredBy') }}
            <a href="https://muehlemann-popp.ch">
              <img
                :src="require('@/assets/Mühlemann&Popp.svg')"
                style="width: 200px; margin-top: 5px"
              />
            </a>
          </div>
        </transition>
      </div>
      <div
        ref="centerButton"
        v-tooltip="{
          content: $t('tooltipCenterButton'),
          trigger: 'hover',
          placement: 'left',
        }"
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
        v-tooltip="{
          content: $t('tooltipSeeAll'),
          trigger: 'hover',
          placement: 'left',
        }"
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
            {{ $t('travelTime') }}:
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
      v-if="$store.getters.raceTrackUnderEditId"
      :map="map"
    ></CourseEditor>
  </div>
</template>
<script>
import MarkerClusterer from '@googlemaps/markerclustererplus'
import eventPresentation from '@/mixins/eventPresentation'
import { mapGetters } from 'vuex'
import calculateDistance from 'assets/js/calculateDistance'
import _ from 'lodash'

export default {
  mixins: [eventPresentation],
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
  data() {
    return {
      marker: {},
      markerFocused: null,
      locationIdToMarker: {},
      pickedLocationId: 'TG9jYXRpb25Ob2RlOjE4NTg=',
      pickedLocation: null,
      // Travel times per location (null == not possible to fetch)
      travelTimes: {},
      formattedTravelDistance: '',
      google: {},
      map: {},
      // TrackOverlays. Key: RaceId
      raceTrackOverlays: {},
    }
  },
  computed: {
    ...mapGetters([
      'mylocation',
      'pickedLocationData',
      'pickedLocationZoomedIn',
      'organizerData',
      'isLoading',
      'raceTrackUnderEditId',
      'raceTrackUnderFocusId',
      'raceTrackUnderHoverId',
      'raceTrackDeletedId',
    ]),
  },
  watch: {
    locations(newlocations, oldlocations) {
      this.updateMarker()
      if (this.countVisibleMarkers() === 0 && newlocations.length > 0) {
        this.seeAll()
      }
      if (newlocations.length === 0) {
        this.$toast.error('No races found. Deactivate some of the filters.')
      }
    },
    /**
     * Update location marker based on currently detected position
     * @param {google.maps.LatLng|google.maps.ReadonlyLatLngLiteral} newLocation
     */
    mylocation(newLocation, oldLocation) {
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
        this.myLocationMarker = new google.maps.Marker({
          icon,
          position: newLocation.latlng,
          map: this.map,
        })
      }
    },
    pickedLocationData(newData, oldData) {
      this.drawRaceTrackOverlays(newData)
    },
    pickedLocationZoomedIn(newData, oldData) {
      this.openLocation(newData)
      this.map.panTo(this.locationIdToMarker[newData].position)
      this.map.setZoom(12)
    },
    raceTrackUnderEditId(newData, oldData) {
      for (const raceId of Object.keys(this.raceTrackOverlays)) {
        const color = newData === raceId ? '#FFFF00' : '#FFFFFF'
        this.raceTrackOverlays[raceId].polyline.setOptions({
          strokeColor: color,
        })
      }
    },
    raceTrackUnderHoverId(newData, oldData) {
      // Called when one hovers over a racetrack
      this.highlightRacetrack(newData)
    },
    raceTrackUnderFocusId(newData, oldData) {
      // Called when one *clicks* on a racetrack
      this.highlightRacetrack(newData)

      if (newData && this.raceTrackOverlays[newData]) {
        // get bounds of racetrack
        google.maps.Polyline.prototype.getBounds = function () {
          const bounds = new google.maps.LatLngBounds()
          this.getPath().forEach(function (item, index) {
            bounds.extend(new google.maps.LatLng(item.lat(), item.lng()))
          })
          return bounds
        }
        this.map.fitBounds(
          this.raceTrackOverlays[newData].polyline.getBounds(),
          {
            top: window.innerHeight / 10,
            left: window.innerWidth / 10,
            bottom: window.innerHeight / 10,
            right: window.innerWidth / 10,
          }
        )
      }
    },
    raceTrackDeletedId(newData, oldData) {
      this.raceTrackOverlays[newData].label.setMap(null)
      this.raceTrackOverlays[newData].polylined.setMap(null)
    },
  },
  mounted() {
    let center
    if (
      this.$router.currentRoute.query.lat &&
      this.$router.currentRoute.query.lng
    ) {
      center = this.mylocation.latlng = {
        lat: parseFloat(this.$router.currentRoute.query.lat),
        lng: parseFloat(this.$router.currentRoute.query.lng),
      }
    } else if (this.mylocation.latlng.lat && this.mylocation.latlng.lng) {
      center = this.mylocation.latlng
    } else {
      // fallback to switzerland
      center = { lat: 47.3474476, lng: 8.6733976 }
    }
    this.map = new google.maps.Map(document.getElementById('map'), {
      center,
      zoom: this.$router.currentRoute.query.zoom
        ? parseInt(this.$router.currentRoute.query.zoom)
        : 5,
      disableDefaultUI: false,
      mapTypeId: this.$store.getters.mapType
        ? this.$store.getters.mapType
        : google.maps.MapTypeId.HYBRID,
      gestureHandling: 'greedy',
      mapTypeControlOptions: {
        style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
        position: google.maps.ControlPosition.TOP_RIGHT,
      },
    })
    this.map.controls[google.maps.ControlPosition.RIGHT].push(
      this.$refs.centerButton
    )
    this.map.controls[google.maps.ControlPosition.RIGHT].push(
      this.$refs.seeAllButton
    )
    this.map.controls[google.maps.ControlPosition.BOTTOM_CENTER].push(
      this.$refs.sponsor
    )
    this.updateMarker()
    if (this.$route.query.location) {
      this.openLocation(this.$route.query.location)
    }

    this.map.addListener('zoom_changed', () => {
      this.zoomChanged()
    })

    this.map.addListener('center_changed', () => {
      this.centerChanged()
    })

    // this is set by the query string "event"
    const zoomedInLocation = this.$store.getters.pickedLocationZoomedIn
    if (zoomedInLocation) {
      // This makes sure that the map is not recentered or rezoomed on every
      // click of a location
      if (!this.$router.currentRoute.query.zoom) {
        this.map.panTo(this.locationIdToMarker[zoomedInLocation].position)
        this.map.setZoom(12)
      }
      this.openLocation(zoomedInLocation)
    }

    // filter by organization --> pan so that all markers are seen
    if (this.organizerData) {
      this.drawRaceTrackOverlaysForEachVisibleLocation()
      if (!this.$router.currentRoute.query.zoom) {
        this.seeAll()
      }
    }
    // see https://forum.vuejs.org/t/lodash-debounce-not-working-when-placed-inside-a-method/86334/3
    this.centerChanged = _.debounce(this.centerChanged, 2000)
  },
  methods: {
    countVisibleMarkers() {
      const bounds = this.map.getBounds()
      let count = 0

      Object.keys(this.marker).forEach((k) => {
        const marker = this.marker[k]
        if (bounds.contains(marker.getPosition()) === true) {
          count++
        }
      })
      return count
    },
    seeAll() {
      /* Expand map to see all markers */
      const bounds = new self.google.maps.LatLngBounds()
      this.locations.forEach(function (item, index) {
        bounds.extend(new self.google.maps.LatLng(item.lat, item.lng))
      })
      this.map.fitBounds(bounds, {
        top: window.innerHeight / 10,
        left: window.innerWidth / 10,
        bottom: window.innerHeight / 10,
        right: window.innerWidth / 10,
      })
    },
    async centerMap() {
      await this.$store.dispatch('locateMe')

      if (this.mylocation.latlng.lat && this.mylocation.latlng.lng) {
        const myLatLng = new google.maps.LatLng(
          this.mylocation.latlng.lat,
          this.mylocation.latlng.lng
        )
        this.map.panTo(myLatLng)
      }
    },
    markerPin(rating = 0) {
      return {
        url: require(`@/assets/markers/Marker${rating}.png`),
        scaledSize: new google.maps.Size(168 / 2, 92 / 2),
        anchor: new google.maps.Point(28 / 2, 70 / 2),
      }
    },
    formatRaceDistances(races) {
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
        .map((e) => this.humanizeDistance(e))
        .filter(onlyUnique)
        .join(', ')
    },
    updateMarker() {
      const infowindow = new google.maps.InfoWindow({
        content: this.$refs.eventDescription,
        fontFamily: "'Source Sans Pro', sans-serif",
        pixelOffset: new google.maps.Size(-54 / 2, 0),
      })

      if (this.markerCluster) {
        this.markerCluster.clearMarkers()
      }

      for (const id of Object.keys(this.marker)) {
        this.marker[id].setMap(null)
        delete this.marker[id]
      }

      for (const location of this.locations) {
        if (!(location.lat && location.lng)) {
          // latLng is mandatory
          continue
        }

        const ratingForMarker = location.averageRating
          ? Math.round(location.averageRating)
          : 0

        const markerObj = new google.maps.Marker({
          icon: this.markerPin(ratingForMarker),
          position: location,
          map: this.map,
          title: location.name,
          shape: { coords: [0, 0, 28, 70 / 2], type: 'rect' },
        })

        this.locationIdToMarker[location.id] = markerObj

        markerObj.addListener('click', () => {
          this.$store.commit('pickedLocationId', location.id)
          this.$emit('locationPicked')
          this.$gtag('event', 'locationPicked', location.id)
          this.pickedLocationId = location.id
          this.pickedLocation = location
          this.location = location
          this.markerObj = markerObj
          infowindow.close()
          this.calculateDistance(this.location, () => {
            this.formattedTravelDistance = this.getFormattedTravelDistance(
              location,
              'DRIVING'
            )
            infowindow.open(this.map, this.markerObj)
          })
        })

        this.marker[location.id] = markerObj
      }
      this.markerCluster = new MarkerClusterer(this.map, this.marker, {
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
    },
    calculateDistance(location, callback) {
      calculateDistance(google, location, this.$store, callback)
    },
    openLocation(id) {
      google.maps.event.trigger(this.locationIdToMarker[id], 'click')
    },
    centerChanged() {
      if (this.map) {
        const query = {}
        query.lat = this.map.getCenter().lat()
        query.lng = this.map.getCenter().lng()
        this.$urlHistory.push(query, null)
      }
    },
    zoomChanged() {
      // hide labels if zoomed out
      for (const raceId of Object.keys(this.raceTrackOverlays)) {
        this.raceTrackOverlays[raceId].label.setVisible(this.isLabelVisible())
      }
      const query = { zoom: this.map.getZoom() }
      this.$urlHistory.push(query, null)
    },
    drawRaceTrackOverlays(location) {
      // Draw Race Track Overlays
      location.allEvents.edges.forEach((event) => {
        event.node.races.edges.forEach((race) => {
          if (
            race.node.coordinates &&
            race.node.coordinates.length > 0 &&
            !(race.node.id in this.raceTrackOverlays)
          ) {
            const coordinateObj = race.node.coordinates

            const coords = coordinateObj.map((i) => {
              return {
                lat: i[0],
                lng: i[1],
              }
            })

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
              map: this.map,
              icon:
                'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
              label: {
                className: 'marker-passive ' + positionClass,
                color: 'white',
                text: this.humanizeDistance(race.node.distance),
                fontSize: '12px',
              },
              visible: this.isLabelVisible(),
            }

            // add a marker without icon to achieve a label
            const label = new google.maps.Marker(labelOptions)

            raceTrackOverlay.setMap(this.map)
            this.raceTrackOverlays[race.node.id] = {
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
    },
    drawRaceTrackOverlaysForEachVisibleLocation() {
      // triggers the loading of each location detail.
      this.locations.forEach((location) => {
        const c = this.$queries.location(
          location.id,
          this.$store.getters.keyword,
          this.$store.getters.dateRange
        )
        c.then((l) => this.drawRaceTrackOverlays(l.data))
      })
    },
    isLabelVisible() {
      const zoom = this.map.getZoom()
      return zoom > 9
    },
    highlightRacetrack(id) {
      for (const raceId of Object.keys(this.raceTrackOverlays)) {
        const po = this.raceTrackOverlays[raceId].polylineOptions
        const lo = this.raceTrackOverlays[raceId].labelOptions
        if (id === raceId) {
          po.strokeOpacity = 1
          po.icons.forEach((i) => (i.icon.fillOpacity = 1))
          lo.label.className = 'marker-active ' + lo.positionClass
        } else {
          po.strokeOpacity = 0.5
          po.icons.forEach((i) => (i.icon.fillOpacity = 0))
          lo.label.className = 'marker-passive ' + lo.positionClass
        }
        this.raceTrackOverlays[raceId].polyline.setOptions(po)
        this.raceTrackOverlays[raceId].label.setOptions(lo)
      }
    },
  },
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
