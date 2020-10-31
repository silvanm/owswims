<template>
  <client-only placeholder="Loading...">
    <vue-slider
      ref="slider"
      v-model="dateRange"
      dotSize="25"
      :min="-6 * 30"
      :max="12 * 30"
      tooltip="always"
      :tooltip-formatter="tooltipFormatter"
      @change="(v) => $emit('change', v)"
    ></vue-slider>
  </client-only>
</template>

<script>
import { addDays, format } from 'date-fns'

export default {
  name: 'DaterangeSlider',
  data() {
    return {
      dateRange: [-6 * 30, 6 * 30],
    }
  },
  methods: {
    tooltipFormatter(val) {
      const d = addDays(new Date(), val)
      return format(d, 'd. LLL yyyy')
    },
  },
}
</script>

<style scoped></style>
