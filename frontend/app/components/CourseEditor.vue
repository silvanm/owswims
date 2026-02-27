<template>
  <div id="drawing-controls" ref="drawingcontrols">
    <button @click="cancelEdit">Close</button>
    <button @click="deleteTrack">Delete</button>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import gql from 'graphql-tag'
import { useMutation } from '@vue/apollo-composable'

const props = defineProps({
  map: {
    default: null,
    type: Object,
  },
})

const store = useMainStore()
const drawingcontrols = ref(null)
let drawingManager = null

const UPDATE_RACE_MUTATION = gql`
  mutation ($id: ID!, $coordinates: [Float]!) {
    updateRace(input: { id: $id, coordinates: $coordinates }) {
      race {
        coordinates
      }
    }
  }
`

const { mutate: updateRaceMutation } = useMutation(UPDATE_RACE_MUTATION)

onMounted(() => {
  drawingManager = new google.maps.drawing.DrawingManager({
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

  props.map.controls[google.maps.ControlPosition.TOP_CENTER].push(
    drawingcontrols.value
  )

  google.maps.event.addListener(
    drawingManager,
    'polylinecomplete',
    (polyline) => {
      const coordinates = []
      polyline
        .getPath()
        .getArray()
        .forEach((o) => {
          coordinates.push(o.lat(), o.lng())
        })
      saveTrack(coordinates)
    }
  )
  drawingManager.setMap(props.map)

  console.log(
    'Click on the map to add waypoints. Double-click to save the track. Drag to move the map.'
  )
})

onBeforeUnmount(() => {
  if (drawingManager) {
    drawingManager.setMap(null)
  }
})

function cancelEdit() {
  store.raceTrackUnderEditId = null
}

function deleteTrack() {
  saveTrack([])
  store.raceTrackDeletedId = store.raceTrackUnderEditId
  console.log('Track deleted')
}

async function saveTrack(coordinateStream) {
  store.isLoading = true
  await updateRaceMutation({
    id: store.raceTrackUnderEditId,
    coordinates: coordinateStream,
  })
  store.isLoading = false
  console.log('Track saved')
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
