<template>
  <div
    id="map"
    style="position: absolute; top: 0; left: 0; height: 100vh; width: 100vw"
  ></div>
</template>

<script>
import { Loader } from 'google-maps'
import MarkerClusterer from '@googlemaps/markerclustererplus'

export default {
  props: {
    events: {
      type: Array,
      default: () => {
        return []
      },
    },
  },
  data() {
    return {
      marker: {},
    }
  },
  watch: {
    events(oldEvents, newEvents) {
      this.updateMarker()
    },
  },
  async mounted() {
    const loader = new Loader('AIzaSyBJm1Vv5sZa0ZlRZ4-vxNSQQydMwXDPzZw', {})

    this.google = await loader.load()
    this.map = new this.google.maps.Map(document.getElementById('map'), {
      center: { lat: 47.3474476, lng: 8.6733976 },
      zoom: 5,
      disableDefaultUI: false,
      mapTypeId: 'satellite',
    })

    this.updateMarker()
  },
  methods: {
    updateMarker() {
      if (this.markerCluster) {
        this.markerCluster.clearMarkers()
      }

      const displayedIds = Object.keys(this.marker)
      const requiredIds = this.events.map((e) => e.node.id)

      // remove events displayed but not in the input anymore
      for (const id of displayedIds) {
        if (!requiredIds.includes(id)) {
          this.marker[id].setMap(null)
          delete this.marker[id]
        }
      }

      // search for events not displayed yet and add them
      for (const event of this.events) {
        if (!displayedIds.includes(event.node.id)) {
          const markerObj = new this.google.maps.Marker({
            position: event.node.location,
            map: this.map,
            title: event.node.name,
          })
          const infowindow = new this.google.maps.InfoWindow({
            content: `${event.node.name}<br>${event.node.location.city} `,
          })

          markerObj.addListener('click', () => {
            infowindow.open(this.map, markerObj)
          })
          this.marker[event.node.id] = markerObj
        }
      }
      this.markerCluster = new MarkerClusterer(this.map, this.marker, {
        imagePath:
          'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m',
      })
    },
  },
}
</script>

<style scoped></style>
