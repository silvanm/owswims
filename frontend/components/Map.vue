<template>
  <div>
    <div ref="eventDescription">
      <div v-if="pickedEvent">
        <h1 class="text-xl font-semibold">
          {{ pickedEvent.city }}, {{ pickedEvent.country }}
        </h1>
        <span v-if="mylocation.lat">
          Travel time: {{ getFormattedTravelDistance(pickedEvent, 'DRIVING') }}
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
    <div id="map"></div>
  </div>
</template>
<script>
import MarkerClusterer from '@googlemaps/markerclustererplus'
import eventPresentation from '@/mixins/eventPresentation'
import { mapGetters } from 'vuex'
import calculateDistance from 'assets/js/calculateDistance'

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
      pickedLocationId: 'TG9jYXRpb25Ob2RlOjE4NTg=',
      pickedLocation: null,
      // Stores travel times per location (null == not possible to fetch)
      travelTimes: {},
      formattedTravelDistance: '',
      isLoading: false,
    }
  },
  computed: {
    ...mapGetters(['mylocation', 'pickedLocationData']),
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
          anchor: new this.google.maps.Point(0, 0),
          strokeWeight: 1,
          strokeColor: '#fff',
          scale: 0.25,
        }
        this.myLocationMarker = new this.google.maps.Marker({
          icon,
          position: newLocation.latlng,
          map: this.map,
        })
      }
    },
  },
  async mounted() {
    this.google = await this.$google()
    let center
    if (this.mylocation.latlng.lat && this.mylocation.latlng.lng) {
      center = this.mylocation.latlng
    } else {
      // fallback to switzerland
      center = { lat: 47.3474476, lng: 8.6733976 }
    }

    this.map = new this.google.maps.Map(document.getElementById('map'), {
      center,
      zoom: 5,
      disableDefaultUI: false,
      mapTypeId: 'satellite',
      gestureHandling: 'greedy',
      mapTypeControl: false,
    })
    this.updateMarker()
  },
  methods: {
    markerPin() {
      return {
        path:
          'M66.9,41.8c0-11.3-9.1-20.4-20.4-20.4c-11.3,0-20.4,9.1-20.4,20.4c0,11.3,20.4,32.4,20.4,32.4S66.9,53.1,66.9,41.8z    M37,41.4c0-5.2,4.3-9.5,9.5-9.5c5.2,0,9.5,4.2,9.5,9.5c0,5.2-4.2,9.5-9.5,9.5C41.3,50.9,37,46.6,37,41.4z',
        fillColor: '#fff',
        fillOpacity: 1,
        anchor: new this.google.maps.Point(50, 70),
        strokeWeight: 0,
        scale: 0.7,
      }
    },
    centerMap() {
      if (this.latlng.mylocation.lat && this.mylocation.latlng.lng) {
        const myLatLng = new this.google.maps.LatLng(
          this.latlng.mylocation.lat,
          this.latlng.mylocation.lng
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
      const infowindow = new this.google.maps.InfoWindow({
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

        const markerObj = new this.google.maps.Marker({
          icon: this.markerPin(),
          position: location,
          map: this.map,
          title: location.name,
        })

        markerObj.addListener('click', () => {
          this.$store.commit('pickedLocationId', location.id)
          this.$emit('locationPicked')
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
    async calculateDistance(location, callback) {
      const google = await this.$google()
      calculateDistance(google, location, this.$store, callback)
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
