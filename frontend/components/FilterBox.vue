<template>
  <div id="filter">
    <div class="bg-white p-4 lg:p-6 relative overflow-hidden">
      <Ribbon v-if="!filterCollapsed">alpha</Ribbon>
      <div class="inline">
        <h1 class="text-xl md:text-2xl font-semibold text-primary">
          ‍️European Open-Water Swims 🏊
          <span class="text-base">
            <CloseButton
              ref="closebutton"
              @collapse="filterCollapsed = true"
              @expand="filterCollapsed = false"
            ></CloseButton>
          </span>
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
      const store = this.$store
      store.commit('isLoading', true)
      navigator.geolocation.getCurrentPosition(
        (position) => {
          store.commit('mylocation', {
            isAccurate: true,
            latlng: {
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            },
          })
          store.commit('isLoading', false)
        },
        () => {
          store.commit('isLoading', false)
        }
      )
    },
    collapse() {
      if (this.$device.isMobile()) {
        this.$refs.closebutton.collapse()
      }
    },
  },
}
</script>
