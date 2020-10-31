<template>
  <div
    id="map"
    style="position: absolute; top: 0; left: 0; height: 100vh; width: 100vw"
  ></div>
</template>

<script>
import { Loader } from 'google-maps'
import MarkerClusterer from '@googlemaps/markerclustererplus'
import { format } from 'date-fns'

export default {
  props: {
    locations: {
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
    locations(oldlocations, newlocations) {
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
    generateInfoWindowStr(location) {
      let s = `<h2><b>${location.city}, ${location.country}</b></h2>`
      // console.log(location)
      for (const event of location.events.edges) {
        const dt = format(new Date(event.node.dateStart), 'E dd. MMM. yyyy')
        s += `<div style="margin-top:10px">${dt}<br><a href="${event.node.website}">${event.node.name}</a></div>`
        s += event.node.races.edges
          .map((e) => e.node.distance.toFixed(1) + 'km')
          .join(', ')
      }
      return s
    },
    updateMarker() {
      if (this.markerCluster) {
        this.markerCluster.clearMarkers()
      }

      const displayedIds = Object.keys(this.marker)
      const requiredIds = this.locations.map((e) => e.node.id)

      // remove locations displayed but not in the input anymore
      for (const id of displayedIds) {
        if (!requiredIds.includes(id)) {
          this.marker[id].setMap(null)
          delete this.marker[id]
        }
      }

      // search for locations not displayed yet and add them
      for (const location of this.locations) {
        if (!displayedIds.includes(location.node.id)) {
          const markerObj = new this.google.maps.Marker({
            position: location.node,
            map: this.map,
            title: location.node.name,
          })
          const infowindow = new this.google.maps.InfoWindow({
            content: this.generateInfoWindowStr(location.node),
          })

          markerObj.addListener('click', () => {
            infowindow.open(this.map, markerObj)
          })
          this.marker[location.node.id] = markerObj
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
