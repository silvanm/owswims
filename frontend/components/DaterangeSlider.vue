<template>
  <client-only placeholder="Loading...">
    <vue-slider
      ref="slider"
      v-model="dateRange"
      dot-size="25"
      :marks="marksFormatter"
      :min="0"
      :max="12"
      :tooltip-formatter="tooltipFormatter"
      @change="(v) => $emit('change', v)"
    ></vue-slider>
  </client-only>
</template>

<script>
import { addMonths, format } from 'date-fns'
import { localeMap } from '../constants'

export default {
  name: 'DaterangeSlider',
  data() {
    return {
      dateRange: [0, 12],
    }
  },
  methods: {
    tooltipFormatter(val) {
      const d = addMonths(new Date(), val)
      return format(d, 'LLL yy', { locale: localeMap[this.$i18n.locale] })
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
