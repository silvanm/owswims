<template>
  <div
    style="
      position: absolute;
      background-color: white;
      top: 0;
      left: 0;
      z-index: 10;
    "
  >
    <button @click="cancelEdit">Cancel</button>
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
    console.log(this.google.maps)
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
  },
  beforeDestroy() {
    this.drawingManager.setMap(null)
  },
  methods: {
    cancelEdit() {
      self.$store.commit('raceTrackUnderEditId', null)
    },
    deleteTrack() {
      this.saveTrack([])
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
    },
  },
}
</script>
