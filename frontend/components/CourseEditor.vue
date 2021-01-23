<template>
  <div ref="drawingcontrols" id="drawing-controls">
    <button @click="cancelEdit">Close</button>
    <button @click="deleteTrack">Delete</button>
  </div>
</template>
<script>
import gql from 'graphql-tag'

export default {
  props: {
    google: {
      type: Object,
    },
    map: {
      type: Object,
    },
  },
  computed: {},
  mounted() {
    this.drawingManager = new this.google.maps.drawing.DrawingManager({
      drawingMode: this.google.maps.drawing.OverlayType.POLYLINE,
      drawingControl: true,
      drawingControlOptions: {
        position: this.google.maps.ControlPosition.TOP_CENTER,
        drawingModes: [this.google.maps.drawing.OverlayType.POLYLINE],
      },
      polylineOptions: {
        strokeColor: '#FFFF00',
        strokeOpacity: 1.0,
        strokeWeight: 2,
      },
    })

    this.map.controls[this.google.maps.ControlPosition.TOP_CENTER].push(
      this.$refs.drawingcontrols
    )

    const self = this

    this.google.maps.event.addListener(
      this.drawingManager,
      'polylinecomplete',
      function (polyline) {
        console.log(polyline)
        const coordinates = []
        polyline
          .getPath()
          .getArray()
          .forEach((o) => {
            coordinates.push(o.lat(), o.lng())
          })
        self.saveTrack(coordinates)

        console.log(coordinates)
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
