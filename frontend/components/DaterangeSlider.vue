<template>
  <client-only placeholder="Loading...">
    <div>
      <div v-if="!showCalendar" class="pl-4 pr-4 pb-8">
        <vue-slider
          ref="slider"
          v-model="dateRangeRelative"
          dot-size="25"
          :marks="marksFormatter"
          :min="0"
          :max="12"
          :tooltip-formatter="tooltipFormatter"
          @change="changeSlider"
        ></vue-slider>
      </div>
      <div v-if="showCalendar" class="pb-8">
        <date-picker
          :value="dateRange"
          range-separator="-"
          :editable="false"
          :clearable="false"
          :open="true"
          :inline="true"
          :lang="lang()"
          range
          @input="datepickerInput"
        ></date-picker>
      </div>
    </div>
  </client-only>
</template>

<script>
import { addMonths, format } from 'date-fns'
import DatePicker from 'vue2-datepicker'
import { localeMap } from '../constants'
import 'vue2-datepicker/index.css'
import 'vue2-datepicker/locale/fr'
import 'vue2-datepicker/locale/en'
import 'vue2-datepicker/locale/de'
import 'vue2-datepicker/locale/es'
import 'vue2-datepicker/locale/ru'
import 'vue2-datepicker/locale/it'

export default {
  name: 'DaterangeSlider',
  components: { DatePicker },
  props: {
    showCalendar: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      dateRangeRelative: [0, 12],
      dateRange: [null, null],
    }
  },
  mounted() {
    this.updateDateRangeFromRelative()
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
    changeSlider(v) {
      this.dateRangeRelative = [v[0], v[1]]
      this.updateDateRangeFromRelative()
    },
    updateDateRangeFromRelative() {
      const today = new Date()
      const newFrom = new Date(
        today.getFullYear(),
        today.getMonth() + this.dateRangeRelative[0],
        1
      )
      const newTo = new Date(
        today.getFullYear(),
        today.getMonth() + this.dateRangeRelative[1],
        1
      )
      this.dateRange = [newFrom, newTo]
      this.emitDate()
    },
    datepickerInput(v) {
      this.dateRange = [v[0], v[1]]
      this.emitDate()
    },
    emitDate() {
      this.$emit('change', [this.dateRange[0], this.dateRange[1]])
    },
    lang() {
      return localeMap[this.$i18n.locale].code
    },
  },
}
</script>

<style>
.mx-datepicker {
  @apply w-full;
}

.mx-datepicker-main {
  font-family: inherit;
  color: black;
}

.mx-btn-text {
  color: black;
}

.mx-input-wrapper input {
  @apply border w-full;
}
</style>
