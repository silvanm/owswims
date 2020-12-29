<template>
  <div id="filter">
    <div class="bg-white p-4 lg:p-6 relative overflow-hidden">
      <Ribbon v-if="!filterCollapsed">beta</Ribbon>
      <div class="inline">
        <h1 class="text-xl md:text-2xl font-semibold text-primary">
          ‍️European Open-Water Swims
          <div class="inline float-right">
            <span class="text-base">
              <span
                v-if="!filterCollapsed"
                class="pr-2 cursor-pointer"
                @click="clickOptionalSearchParamsButton"
              >
                <font-awesome-icon icon="search" size="lg"></font-awesome-icon>
              </span>
              <span class="pr-2 cursor-pointer" @click="clickInfoCircle">
                <font-awesome-icon
                  icon="info-circle"
                  size="lg"
                ></font-awesome-icon>
              </span>
              <CloseButton
                ref="closebutton"
                @collapse="clickCollapseFilter"
                @expand="filterCollapsed = false"
              ></CloseButton>
            </span>
          </div>
        </h1>
      </div>
      <div
        style="transition: max-height 0.5s linear"
        :style="{
          maxHeight: filterCollapsed && !showInfos ? 0 : '500px',
        }"
      >
        <div
          style="transition: max-height 0.5s linear"
          :style="{
            maxHeight: !showInfos ? 0 : '500px',
          }"
          class="overflow-hidden mt-2"
          id="infos"
        >
          <p>
            If you plan your vacations around open-water swim events, then this
            app is for you. Select the desired distance and timerange and all
            matching events will be shown to you. Enable the "Show trip
            duration" switch to let the app calculate you the time to get there
            by car.
          </p>

          <p>
            Additions or corrections can be reported to
            <a href="https://muehlemann.com" target="_blank">me</a> at
            <a href="mailto:silvan@open-water-swims.com"
              >silvan@open-water-swims.com</a
            >.
          </p>

          <p>Thanks to Andrey Shenko for his collaboration.</p>
        </div>
        <!-- Keyword search -->
        <div
          style="transition: max-height 0.5s linear"
          :style="{
            maxHeight: !showOptionalSearchParams ? 0 : '500px',
          }"
          class="overflow-hidden"
          id="optional-search-params"
        >
          <label class="block font-semibold pb-2 pt-4" for="keyword"
            >Keyword search</label
          >
          <input
            id="keyword"
            v-model="keyword"
            type="text"
            class="block border p-2 w-full"
          />
        </div>
        <!-- Search by other parameters -->
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
          @change="(e) => (e ? $store.dispatch('locateMe') : null)"
          ><span id="activate-geolocation">Show trip duration</span></Toggle
        >
        <div v-if="!$device.isMobile()" class="mt-2 text-gray-600">
          Powered by
          <a href="https://muehlemann-popp.ch" target="_blank"
            >Mühlemann&Popp</a
          >
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import 'assets/slider.css'
import CloseButton from '@/components/CloseButton'
import Ribbon from '@/components/Ribbon'
import DaterangeSlider from '@/components/DaterangeSlider'
import Toggle from '@/components/Toggle'

export default {
  components: { Ribbon, CloseButton, DaterangeSlider, Toggle },
  data() {
    return {
      showOptionalSearchParams: false,
      showInfos: false,
      keyword: '',
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
      this.$gtag('event', 'distanceRange', newRange)
      this.$store.commit('distanceRange', newRange)
    },
    keyword(newKeyword, oldKeyword) {
      this.$store.commit('keyword', newKeyword)
      this.$gtag('event', 'keyword', newKeyword)
    },
  },
  async mounted() {
    this.google = await this.$google()
  },
  methods: {
    clickCollapseFilter() {
      this.filterCollapsed = true
      this.showInfos = false
    },
    clickOptionalSearchParamsButton() {
      this.$gtag('event', 'clickOptionalSearchParamsButton')
      if (this.showOptionalSearchParams) {
        this.keyword = ''
      }
      this.showOptionalSearchParams = !this.showOptionalSearchParams
    },
    clickInfoCircle() {
      this.showInfos = !this.showInfos
      this.$gtag('event', 'clickInfoCircle')
    },
    updateDateRange(range) {
      this.dateRange = range
      this.$store.commit('dateRange', range)
      this.$gtag('event', 'dateRange', range)
    },
    collapse() {
      if (this.$device.isMobile()) {
        this.$refs.closebutton.collapse()
        this.clickCollapseFilter()
      }
    },
  },
}
</script>
<style lang="scss" scoped>
#filter {
  @apply absolute w-full;
  transition: top 0.5s;

  @screen lg {
    /* on large screen the event pane is attached to the top */
    @apply relative;
    max-width: 500px;
  }
}

p {
  @apply my-2;
}
</style>
