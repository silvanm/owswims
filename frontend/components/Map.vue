<template>
  <div>
    <!-- Containers which will be included in Google Maps. Hiding them by default -->
    <div class="hidden">
      <div
        ref="centerButton"
        class="bg-white"
        style="
          border-radius: 2px;
          margin: 10px;
          height: 40px;
          width: 40px;
          padding: 9px;
        "
      >
        <button class="text-gray-600" @click="centerMap">
          <font-awesome-icon
            icon="location-arrow"
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
            Travel time:
            {{ formattedTravelDistance }}
          </span>
          <div
            v-for="event in pickedLocationData.allEvents.edges"
            :key="event.node.id"
          >
            <div style="margin-top: 10px">
              {{ formatEventDate(event.node.dateStart) }}<br />
              <a :href="event.node.website" class="font-semibold">{{
                event.node.name
              }}</a
              ><br />
              {{ formatRaceDistances(event.node.races) }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <div id="map"></div>
    <CourseEditor
      v-if="$store.getters.raceTrackUnderEditId && google.maps"
      :map="map"
      :google="google"
    ></CourseEditor>
  </div>
</template>
<script>
import MarkerClusterer from '@googlemaps/markerclustererplus'
import eventPresentation from '@/mixins/eventPresentation'
import { mapGetters } from 'vuex'
import calculateDistance from 'assets/js/calculateDistance'
import gql from 'graphql-tag'

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
      // Draw Race Track Overlays
      newData.allEvents.edges.forEach((event) => {
        event.node.races.edges.forEach((race) => {
          if (
            race.node.coordinates &&
            race.node.coordinates.length > 0 &&
            !(race.node.id in this.raceTrackOverlays)
          ) {
            const coordinateObj = race.node.coordinates

            const coordinateArray = coordinateObj.map((i) => {
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
            const numArrows = 6
            for (let i = 0; i < numArrows; i++) {
              icons.push({
                icon: arrowSymbol,
                offset: ((100 / numArrows) * i).toString() + '%',
              })
            }

            const options = {
              path: coordinateArray,
              geodesic: true,
              strokeColor: '#FFFFFF',
              strokeOpacity: 0.5,
              strokeWeight: 3,
              icons,
            }

            const raceTrackOverlay = new google.maps.Polyline(options)

            // take the middle coordinate and apply a label there
            const middleCoordinate =
              coordinateArray[Math.floor(coordinateArray.length / 2)]

            // add a marker without icon to achieve a label
            const label = new google.maps.Marker({
              position: middleCoordinate,
              map: this.map,
              icon:
                'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
              label: {
                color: '#FFFFFF',
                text: this.humanizeDistance(race.node.distance),
                fontSize: '12px',
              },
            })

            raceTrackOverlay.setMap(this.map)
            this.raceTrackOverlays[race.node.id] = {
              polyline: raceTrackOverlay,
              // did not find out how I can retrieve the options from an existing polyline
              // so I can modify them. That's why I am storing the option object
              polylineOptions: options,
              label,
            }
          }
        })
      })
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
        const self = this
        google.maps.Polyline.prototype.getBounds = function () {
          const bounds = new self.google.maps.LatLngBounds()
          this.getPath().forEach(function (item, index) {
            bounds.extend(new self.google.maps.LatLng(item.lat(), item.lng()))
          })
          return bounds
        }
        this.map.fitBounds(
          this.raceTrackOverlays[newData].polyline.getBounds(),
          { top: 100, left: 50, bottom: 100, right: 50 }
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
    if (this.mylocation.latlng.lat && this.mylocation.latlng.lng) {
      center = this.mylocation.latlng
    } else {
      // fallback to switzerland
      center = { lat: 47.3474476, lng: 8.6733976 }
    }
    this.map = new google.maps.Map(document.getElementById('map'), {
      center,
      zoom: 5,
      disableDefaultUI: false,
      mapTypeId: google.maps.MapTypeId.HYBRID,
      gestureHandling: 'greedy',
      mapTypeControlOptions: {
        style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
        position: google.maps.ControlPosition.TOP_RIGHT,
      },
    })
    this.map.controls[google.maps.ControlPosition.RIGHT].push(
      this.$refs.centerButton
    )
    this.updateMarker()
    if (this.$route.query.location) {
      this.openLocation(this.$route.query.location)
    }
    if (this.$route.query.event) {
      this.openLocationBySlug(this.$route.query.event)
    }

    this.map.addListener('zoom_changed', () => {
      this.zoomChanged()
    })
  },
  methods: {
    markerPin() {
      return {
        path:
          'M66.9,41.8c0-11.3-9.1-20.4-20.4-20.4c-11.3,0-20.4,9.1-20.4,20.4c0,11.3,20.4,32.4,20.4,32.4S66.9,53.1,66.9,41.8z    M37,41.4c0-5.2,4.3-9.5,9.5-9.5c5.2,0,9.5,4.2,9.5,9.5c0,5.2-4.2,9.5-9.5,9.5C41.3,50.9,37,46.6,37,41.4z',
        fillColor: '#fff',
        fillOpacity: 1,
        anchor: new google.maps.Point(50, 70),
        strokeWeight: 0,
        scale: 0.7,
      }
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
    formatRaceDistances(races) {
      return races.edges
        .map((e) => this.humanizeDistance(e.node.distance))
        .join(', ')
    },
    updateMarker() {
      const infowindow = new google.maps.InfoWindow({
        content: this.$refs.eventDescription,
        fontFamily: "'Source Sans Pro', sans-serif",
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

        const markerObj = new google.maps.Marker({
          icon: this.markerPin(),
          position: location,
          map: this.map,
          title: location.name,
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
      })
    },
    calculateDistance(location, callback) {
      calculateDistance(google, location, this.$store, callback)
    },
    openLocation(id) {
      this.map.panTo(this.locationIdToMarker[id].position)
      this.map.setZoom(14)
      google.maps.event.trigger(this.locationIdToMarker[id], 'click')
    },
    async openLocationBySlug(slug) {
      // @todo move this to VueX?
      const result = await this.$apollo.query({
        query: gql`
          query($slug: String!) {
            allEvents(slug: $slug) {
              edges {
                node {
                  id
                  location {
                    id
                  }
                }
              }
            }
          }
        `,
        variables: {
          slug,
        },
      })
      this.$store.commit('focusedEventId', result.data.allEvents.edges[0].node)
      this.openLocation(result.data.allEvents.edges[0].node.location.id)
    },
    zoomChanged() {
      const zoom = this.map.getZoom()
      // hide labels if zoomed out
      for (const raceId of Object.keys(this.raceTrackOverlays)) {
        this.raceTrackOverlays[raceId].label.setVisible(zoom > 9)
      }
    },
    setArrowVisibilityAccordingToZoomLevel() {
      const zoom = this.map.getZoom()
      for (const raceId of Object.keys(this.raceTrackOverlays)) {
        console.log(this.raceTrackOverlays[raceId].polyline.options)
        if (zoom < 9) {
        }
      }
    },
    highlightRacetrack(id) {
      for (const raceId of Object.keys(this.raceTrackOverlays)) {
        const po = this.raceTrackOverlays[raceId].polylineOptions
        if (id === raceId) {
          po.strokeOpacity = 1
          po.icons.forEach((i) => (i.icon.fillOpacity = 1))
        } else {
          po.strokeOpacity = 0.5
          po.icons.forEach((i) => (i.icon.fillOpacity = 0))
        }
        this.raceTrackOverlays[raceId].polyline.setOptions(po)
      }
    },
  },
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
</style>
