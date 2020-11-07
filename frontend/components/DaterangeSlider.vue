<template>
  <client-only placeholder="Loading...">
    <vue-slider
      ref="slider"
      v-model="dateRange"
      dot-size="25"
      :marks="marksFormatter"
      :min="-6"
      :max="12"
      :tooltip-formatter="tooltipFormatter"
      @change="(v) => $emit('change', v)"
    ></vue-slider>
  </client-only>
</template>

<script>
import { addMonths, format } from 'date-fns'

export default {
  name: 'DaterangeSlider',
  data() {
    return {
      dateRange: [-6, 6],
    }
  },
  methods: {
    tooltipFormatter(val) {
      const d = addMonths(new Date(), val)
      return format(d, 'LLL yy')
    },
    marksFormatter(val) {
      if (val % 3 === 0) {
        return { label: this.tooltipFormatter(val) }
      }
      return false
    },
  },
}
</script>

<style scoped></style>
