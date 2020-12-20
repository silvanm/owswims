<template>
  <div id="filter">
    <div class="bg-white p-4 md:p-6 relative overflow-hidden">
      <Ribbon v-if="!filterCollapsed">alpha</Ribbon>
      <div class="inline">
        <h1 class="text-xl md:text-2xl font-semibold text-primary">
          ‍️European Open-Water Swims 🏊
          <CloseButton
            @collapse="filterCollapsed = true"
            @expand="filterCollapsed = false"
          ></CloseButton>
        </h1>
      </div>
      <div
        style="transition: max-height 0.5s linear"
        :style="{ maxHeight: filterCollapsed ? 0 : '500px' }"
      >
        <h2 class="font-semibold pb-2 pt-4">Race Distance</h2>
        <div id="race-distance-slider" class="pl-4 pr-4 pb-5">
          <client-only>
            <vue-slider
              v-model="distanceRange"
              :marks="(val) => val % 5 === 0"
              :tooltip-formatter="(val) => `${val}km`"
              dot-size="25"
              :min="0"
              :max="30"
            ></vue-slider>
          </client-only>
        </div>
        <h2 class="font-semibold pb-2">Date</h2>
        <div id="date-range-slider" class="pl-4 pr-4 pb-8">
          <DaterangeSlider @change="updateDateRange"></DaterangeSlider>
        </div>
        <Toggle
          name="locateMe"
          :is-checked="geoLocationEnabled"
          @change="(e) => (e ? locateMe() : null)"
          ><span id="activate-geolocation">Show Travel times</span></Toggle
        >
      </div>
    </div>
  </div>
</template>
<script>
import 'assets/slider.css'
import { Loader } from 'google-maps'
import CloseButton from '@/components/CloseButton'
import Ribbon from '@/components/Ribbon'
import DaterangeSlider from '@/components/DaterangeSlider'
import Toggle from '@/components/Toggle'

export default {
  components: { Ribbon, CloseButton, DaterangeSlider, Toggle },
  data() {
    return {
      distanceRange: [0, 30],
      // @todo: this must be applied to the slider
      dateRange: [0, 12],
      lat: null,
      lng: null,
      geoLocationEnabled: false,
      filterCollapsed: false,
      isLoading: false,
    }
  },
  watch: {
    distanceRange(newRange, oldRange) {
      this.$store.commit('distanceRange', newRange)
    },
  },
  async mounted() {
    const loader = new Loader(process.env.googleMapsKey, { version: 'beta' })
    this.google = await loader.load()
  },
  methods: {
    updateDateRange(range) {
      this.dateRange = range
      this.$store.commit('dateRange', range)
    },
    locateMe() {
      console.log('Locating me')
      this.isLoading = true
      const store = this.$store
      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log(
            `storing position lat=${position.coords.latitude}, lng=${position.coords.longitude}`
          )
          store.commit('mylocation', {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          })
          this.isLoading = false
        },
        () => {
          this.isLoading = false
          console.log('Geolocation has failed')
        }
      )
    },
  },
}
</script>
