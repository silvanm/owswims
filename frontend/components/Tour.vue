<template>
  <div>
    <v-tour name="myTour" :steps="steps"></v-tour>
  </div>
</template>

<script>
export default {
  name: 'Tour',
  data() {
    return {
      steps: [
        {
          target: '#race-distance-slider',
          content: `Choose the desired race distance`,
        },
        {
          target: '#date-range-slider',
          content: 'Filter by date',
        },
        {
          target: '#activate-geolocation',
          content: 'Enable this switch to display travel times',
        },
      ],
    }
  },
  mounted() {
    // this.$tours.myTour.start()
  },
}
</script>
