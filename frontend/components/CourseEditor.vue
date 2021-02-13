<template>
  <div id="drawing-controls" ref="drawingcontrols">
    <button @click="cancelEdit">Close</button>
    <button @click="deleteTrack">Delete</button>
  </div>
</template>
<script>
import gql from 'graphql-tag'

export default {
  props: {
    map: {
      default: null,
      type: Object,
    },
  },
  computed: {},
  mounted() {
    this.drawingManager = new google.maps.drawing.DrawingManager({
      drawingMode: google.maps.drawing.OverlayType.POLYLINE,
      drawingControl: true,
      drawingControlOptions: {
        position: google.maps.ControlPosition.TOP_CENTER,
        drawingModes: [google.maps.drawing.OverlayType.POLYLINE],
      },
      polylineOptions: {
        strokeColor: '#FFFF00',
        strokeOpacity: 1.0,
        strokeWeight: 2,
      },
    })

    this.map.controls[google.maps.ControlPosition.TOP_CENTER].push(
      this.$refs.drawingcontrols
    )

    const self = this

    google.maps.event.addListener(
      this.drawingManager,
      'polylinecomplete',
      function (polyline) {
        const coordinates = []
        polyline
          .getPath()
          .getArray()
          .forEach((o) => {
            coordinates.push(o.lat(), o.lng())
          })
        self.saveTrack(coordinates)
      }
    )
    this.drawingManager.setMap(this.map)

    this.$toast.success(
      'Click on the map to add waypoints. Double-click to save the track. Drag to move the map.'
    )
  },
  beforeDestroy() {
    this.drawingManager.setMap(null)
  },
  methods: {
    initMeasurementFunctions() {
      google.maps.LatLng.prototype.kmTo = function (a) {
        const e = Math
        const ra = e.PI / 180
        const b = this.lat() * ra
        const c = a.lat() * ra
        const d = b - c
        const g = this.lng() * ra - a.lng() * ra
        const f =
          2 *
          e.asin(
            e.sqrt(
              e.pow(e.sin(d / 2), 2) +
                e.cos(b) * e.cos(c) * e.pow(e.sin(g / 2), 2)
            )
          )
        return f * 6378.137
      }

      google.maps.Polyline.prototype.inKm = function (n) {
        const a = this.getPath(n)
        const len = a.getLength()
        let dist = 0
        for (let i = 0; i < len - 1; i++) {
          dist += a.getAt(i).kmTo(a.getAt(i + 1))
        }
        return dist
      }
    },
    cancelEdit() {
      this.$store.commit('raceTrackUnderEditId', null)
    },
    deleteTrack() {
      this.saveTrack([])
      this.$store.commit(
        'raceTrackDeletedId',
        this.$store.getters.raceTrackUnderEditId
      )
      this.$toast.success('Track deleted')
    },
    async saveTrack(coordinateStream) {
      this.$store.commit('isLoading', true)
      await this.$apollo.mutate({
        mutation: gql`
          mutation($id: ID!, $coordinates: [Float]!) {
            updateRace(input: { id: $id, coordinates: $coordinates }) {
              race {
                coordinates
              }
            }
          }
        `,
        // Parameters
        variables: {
          id: this.$store.getters.raceTrackUnderEditId,
          coordinates: coordinateStream,
        },
      })
      this.$store.commit('isLoading', false)
      this.$toast.success('Track saved')
    },
  },
}
</script>
<style lang="scss">
#drawing-controls {
  margin: 5px;

  button {
    @apply bg-white font-bold cursor-pointer m-0 p-1;
    height: 24px;
  }
}
</style>
