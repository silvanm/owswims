<template>
  <ClientOnly fallback-tag="span" fallback="Loading...">
    <div>
      <div v-if="!showCalendar" class="pl-4 pr-4 pb-8">
        <VueSlider
          v-model="dateRangeRelative"
          :dot-size="25"
          :marks="marksFormatter"
          :min="-1"
          :max="11"
          :tooltip-formatter="tooltipFormatter"
          @change="changeSlider"
        />
      </div>
      <div v-if="showCalendar" class="pb-8">
        <VueDatePicker
          v-model="dateRange"
          range
          inline
          auto-apply
          :enable-time-picker="false"
          :locale="currentLocale"
          @update:model-value="datepickerInput"
        />
      </div>
    </div>
  </ClientOnly>
</template>

<script>
import { addMonths, format } from 'date-fns'
import { de, enUS, fr, it, ru, es, ja } from 'date-fns/locale'
import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/default.css'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

const localeMap = { en: enUS, de, fr, it, ru, es, ja }

export default {
  name: 'DaterangeSlider',
  components: { VueSlider, VueDatePicker },
  props: {
    showCalendar: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['change'],
  setup() {
    const { locale } = useI18n()
    return { locale }
  },
  data() {
    return {
      dateRangeRelative: [-1, 11],
      dateRange: [null, null],
    }
  },
  computed: {
    currentLocale() {
      return localeMap[this.locale] || enUS
    },
  },
  mounted() {
    this.updateDateRangeFromRelative()
  },
  methods: {
    tooltipFormatter(val) {
      const d = addMonths(new Date(), val)
      return format(d, 'LLL yyyy', { locale: localeMap[this.locale] || enUS })
    },
    marksFormatter(val) {
      if (val % 3 === 0) {
        const d = addMonths(new Date(), val)
        return {
          label: format(d, 'LLL yyyy', { locale: localeMap[this.locale] || enUS }),
        }
      }
      return false
    },
    changeSlider() {
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
      if (v && v.length === 2) {
        this.dateRange = [v[0], v[1]]
        this.emitDate()
      }
    },
    emitDate() {
      this.$emit('change', [this.dateRange[0], this.dateRange[1]])
    },
  },
}
</script>

<style>
/* VueDatePicker overrides */
.dp__main {
  font-family: inherit;
}
</style>
