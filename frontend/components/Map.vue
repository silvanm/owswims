<template>
  <div id="map" style="width: 1000px; height: 500px"></div>
</template>

<script>
import { Loader } from 'google-maps'

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
      marker: [],
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
      zoom: 7,
      disableDefaultUI: false,
      mapTypeId: 'satellite',
    })

    this.updateMarker()
  },
  methods: {
    updateMarker() {
      this.marker.forEach((m) => {
        m.setMap(null)
      })
      this.events.forEach((event) => {
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
        this.marker.push(markerObj)
      })
    },
  },
}
</script>

<style scoped></style>
