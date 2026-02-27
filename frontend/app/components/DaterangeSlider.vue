<template>
  <ClientOnly fallback-tag="span" fallback="Loading...">
    <div>
      <div v-if="!showCalendar" class="pl-4 pr-4 pb-8">
        <!-- Dual range slider replacing vue-slider-component -->
        <div class="relative pt-6 pb-2">
          <div class="flex justify-between text-xs text-gray-500 mb-2">
            <span>{{ tooltipFormatter(min) }}</span>
            <span>{{ tooltipFormatter(max) }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs whitespace-nowrap">{{ tooltipFormatter(dateRangeRelative[0]) }}</span>
            <input
              type="range"
              :min="min"
              :max="max"
              :value="dateRangeRelative[0]"
              class="w-full"
              @input="onFromChange($event.target.value)"
            />
            <input
              type="range"
              :min="min"
              :max="max"
              :value="dateRangeRelative[1]"
              class="w-full"
              @input="onToChange($event.target.value)"
            />
            <span class="text-xs whitespace-nowrap">{{ tooltipFormatter(dateRangeRelative[1]) }}</span>
          </div>
        </div>
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
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

const localeMap = { en: enUS, de, fr, it, ru, es, ja }

export default {
  name: 'DaterangeSlider',
  components: { VueDatePicker },
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
      min: -1,
      max: 11,
      dateRangeRelative: [-1, 11],
      dateRange: [null, null],
    }
  },
  computed: {
    currentLocale() {
      return this.locale || 'en'
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
    onFromChange(val) {
      const v = parseInt(val)
      if (v < this.dateRangeRelative[1]) {
        this.dateRangeRelative = [v, this.dateRangeRelative[1]]
        this.updateDateRangeFromRelative()
      }
    },
    onToChange(val) {
      const v = parseInt(val)
      if (v > this.dateRangeRelative[0]) {
        this.dateRangeRelative = [this.dateRangeRelative[0], v]
        this.updateDateRangeFromRelative()
      }
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
