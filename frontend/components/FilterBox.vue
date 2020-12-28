<template>
  <div id="filter">
    <div class="bg-white p-4 lg:p-6 relative overflow-hidden">
      <Ribbon v-if="!filterCollapsed">alpha</Ribbon>
      <div class="inline">
        <h1 class="text-xl md:text-2xl font-semibold text-primary">
          ‍️European Open-Water Swims 🏊
          <div class="inline float-right">
            <span class="text-base">
              <span
                class="pr-2 cursor-pointer"
                @click="clickOptionalSearchParamsButton"
              >
                <font-awesome-icon icon="search" size="lg"></font-awesome-icon>
              </span>
              <CloseButton
                ref="closebutton"
                @collapse="filterCollapsed = true"
                @expand="filterCollapsed = false"
              ></CloseButton>
            </span>
          </div>
        </h1>
      </div>
      <div
        style="transition: max-height 0.5s linear"
        :style="{
          maxHeight: filterCollapsed ? 0 : '500px',
        }"
      >
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
          ><span id="activate-geolocation">Show Travel times</span></Toggle
        >
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
      this.$store.commit('distanceRange', newRange)
    },
    keyword(newKeyword, oldKeyword) {
      this.$store.commit('keyword', newKeyword)
    },
  },
  async mounted() {
    this.google = await this.$google()
  },
  methods: {
    clickOptionalSearchParamsButton() {
      if (this.showOptionalSearchParams) {
        this.keyword = ''
      }
      this.showOptionalSearchParams = !this.showOptionalSearchParams
    },
    updateDateRange(range) {
      this.dateRange = range
      this.$store.commit('dateRange', range)
    },
    collapse() {
      if (this.$device.isMobile()) {
        this.$refs.closebutton.collapse()
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
</style>
