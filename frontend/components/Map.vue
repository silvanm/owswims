<template>
  <div>
    <div ref="eventDescription">
      <div v-if="pickedEvent">
        <h1 class="text-xl font-semibold">
          {{ pickedEvent.city }}, {{ pickedEvent.country }}
        </h1>
        Travel time: {{ getFormattedTravelDistance(pickedEvent) }}
        <div v-for="event in pickedEvent.events.edges" :key="event.node.id">
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
    <div
      id="map"
      style="position: absolute; top: 0; left: 0; height: 100vh; width: 100vw"
    ></div>
  </div>
</template>

<script>
import MarkerClusterer from '@googlemaps/markerclustererplus'
import { format, formatDistance } from 'date-fns'

export default {
  props: {
    google: {
      type: Object,
      default: null,
    },
    locations: {
      type: Array,
      default: () => {
        return []
      },
    },
    lat: {
      type: Number,
      default: null,
    },
    lng: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      marker: {},
      pickedEvent: null,
      // Stores travel times per location (null == not possible to fetch)
      travelTimes: {},
    }
  },
  watch: {
    locations(oldlocations, newlocations) {
      this.updateMarker()
    },
    lat() {
      this.centerMap()
    },
    lng() {
      this.centerMap()
    },
  },
  mounted() {
    this.map = new this.google.maps.Map(document.getElementById('map'), {
      center: { lat: 47.3474476, lng: 8.6733976 },
      zoom: 5,
      disableDefaultUI: false,
      mapTypeId: 'satellite',
      mapTypeControl: false,
    })

    this.updateMarker()
  },
  methods: {
    centerMap() {
      if (this.lat && this.lng) {
        const myLatLng = new this.google.maps.LatLng(this.lat, this.lng)
        this.map.panTo(myLatLng)
      }
    },
    formatEventDate(dt) {
      return format(new Date(dt), 'E dd. MMM. yyyy')
    },
    formatRaceDistances(races) {
      return races.edges
        .map((e) => e.node.distance.toFixed(1) + 'km')
        .join(', ')
    },
    getFormattedTravelDistance(location) {
      const k = `${location.lat},${location.lng}`
      if (k in this.travelTimes && this.travelTimes[k] !== null) {
        const formatDuration = (s) => formatDistance(0, s * 1000)

        return `${formatDuration(this.travelTimes[k].duration)} ${(
          this.travelTimes[k].distance / 1000
        ).toFixed(0)}km`
      } else {
        return '?'
      }
    },
    updateMarker() {
      const infowindow = new this.google.maps.InfoWindow({
        content: this.$refs.eventDescription,
      })

      if (this.markerCluster) {
        this.markerCluster.clearMarkers()
      }

      for (const id of Object.keys(this.marker)) {
        this.marker[id].setMap(null)
        delete this.marker[id]
      }

      for (const location of this.locations) {
        const markerObj = new this.google.maps.Marker({
          position: location.node,
          map: this.map,
          title: location.node.name,
        })

        markerObj.addListener('click', () => {
          this.pickedEvent = location.node
          infowindow.open(this.map, markerObj)
        })
        this.marker[location.node.id] = markerObj
      }
      this.markerCluster = new MarkerClusterer(this.map, this.marker, {
        imagePath:
          'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m',
      })
    },
    getLocationsWithinViewport() {
      const b = this.map.getBounds()
      return this.locations.filter((l) => {
        return (
          l.node.lat > b.getSouthWest().lat() &&
          l.node.lat < b.getNorthEast().lat() &&
          l.node.lng > b.getSouthWest().lng() &&
          l.node.lng < b.getNorthEast().lng()
        )
      })
    },
    calculateDistances() {
      const requestedDestinations = []
      // Calculate distance for those destinations within the viewport.
      this.getLocationsWithinViewport()
        .slice(0, 10)
        .forEach((location) => {
          // @todo ask only for those who don't have a measurement.
          const k = `${location.node.lat},${location.node.lng}`
          if (!(k in this.travelTimes)) {
            requestedDestinations.push(k)
          }
        })

      const service = new this.google.maps.DistanceMatrixService()
      console.log(`Requesting ${requestedDestinations.length}`)
      if (requestedDestinations.length === 0) return
      service.getDistanceMatrix(
        {
          origins: [new this.google.maps.LatLng(this.lat, this.lng)],
          destinations: requestedDestinations,
          transitOptions: {
            departureTime: new Date(2020, 8, 1, 8),
          },
          travelMode: this.google.maps.TravelMode.DRIVING,
          unitSystem: this.google.maps.UnitSystem.METRIC,
        },
        (response, status) => {
          if (status !== 'OK') {
            alert('Error was: ' + status)
          } else {
            const results = response.rows[0].elements
            console.log(results)
            for (let j = 0; j < results.length; j++) {
              if (results[j].status === 'OK') {
                this.travelTimes[requestedDestinations[j]] = {
                  distance: results[j].distance.value,
                  duration: results[j].duration.value,
                }
              } else {
                this.travelTimes[requestedDestinations[j]] = null
              }
            }
          }
        }
      )
    },
  },
}
</script>

<style scoped></style>
