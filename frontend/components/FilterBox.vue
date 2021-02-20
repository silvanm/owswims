<template>
  <div id="filter">
    <!-- pb-3 is a hack because the div which can collapse always has a height of 2 -->
    <div class="bg-white p-3 pb-2 lg:p-6 lg:pb-5 relative overflow-hidden">
      <h1 class="text-2xl font-semibold text-primary">
        ‍️<a href="/" style="color: black; text-decoration: none">
          <img
            id="site-logo"
            class="inline"
            :src="require('@/assets/site_logo.svg')"
          />
          open-water-swims.com</a
        >
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
      <transition name="fade">
        <h2 v-if="!filterCollapsed" class="mt-1">{{ $t('tagline') }}</h2>
      </transition>
      <Ribbon v-if="!filterCollapsed">beta</Ribbon>
      <div
        style="transition: max-height 0.5s linear"
        :style="{
          maxHeight: filterCollapsed && !showInfos ? 0 : '500px',
        }"
      >
        <div
          id="infos"
          class="overflow-hidden mt-0"
          style="transition: max-height 0.5s linear"
          :style="{
            maxHeight: !showInfos ? 0 : '500px',
          }"
        >
          <Infotext></Infotext>
          <div class="inline-block cursor-pointer">
            <a
              v-if="$store.getters['auth/loggedIn']"
              class="mr-2"
              @click="$store.dispatch('auth/logout')"
              >{{ $t('logout') }}</a
            >
            <span v-else>
              <a @click="$emit('showLogin')">{{ $t('login') }}</a>
            </span>
          </div>
        </div>
        <!-- Keyword search -->
        <div
          id="optional-search-params"
          style="transition: max-height 0.5s linear"
          :style="{
            maxHeight: !showOptionalSearchParams ? 0 : '500px',
          }"
          class="overflow-hidden"
        >
          <label class="block font-semibold pt-4" for="keyword">
            <div class="pb-2">{{ $t('keywordSearch') }}</div>
            <input
              id="keyword"
              v-model="keyword"
              type="text"
              :placeholder="$t('keywordPlaceholder')"
              class="form-input block border p-2 w-full"
            />
          </label>
          <label class="block font-semibold pb-2 pt-4">
            <div class="pb-2">{{ $t('organizerSerie') }}</div>
            <OrganizerSelector></OrganizerSelector>
          </label>
        </div>
        <!-- Search by other parameters -->
        <h2 class="font-semibold pb-2 pt-3 lg:pt-4">
          {{ $t('raceDistance') }}
        </h2>
        <div id="race-distance-slider" class="pl-4 pr-4 pb-5">
          <client-only>
            <vue-slider
              v-model="distanceRange"
              :marks="rangeSliderMarks()"
              :tooltip-formatter="(val) => `${val}km`"
              dot-size="25"
              :min="0"
              :max="30"
            ></vue-slider>
          </client-only>
        </div>
        <h2 class="font-semibold pb-2">{{ $t('date') }}</h2>
        <div id="date-range-slider" class="pl-4 pr-4 pb-8">
          <DaterangeSlider @change="updateDateRange"></DaterangeSlider>
        </div>
        <Toggle
          name="locateMe"
          :is-checked="geoLocationEnabled"
          @change="(e) => (e ? $store.dispatch('locateMe') : null)"
        >
          <span id="activate-geolocation">{{ $t('showTripDuration') }}</span>
          <span
            v-tooltip="{
              content: $t('showTripDurationTooltip'),
              trigger: 'hover',
            }"
            class="text-gray-800 cursor-pointer"
            ><font-awesome-icon icon="question-circle"
          /></span>
        </Toggle>
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
      // if the slider is at the upper edge, then don't have a limit
      if (newRange[1] === this.distanceRange) {
        newRange[1] = 1000
      }
      this.$store.commit('distanceRange', newRange)
      this.$gtag('event', 'distanceRange')
    },
    keyword(newKeyword, oldKeyword) {
      this.$store.commit('keyword', newKeyword)
      this.$gtag('event', 'keyword')
    },
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
      this.$gtag('event', 'dateRange')
    },
    collapse() {
      if (this.$device.isMobile()) {
        this.$refs.closebutton.collapse()
        this.clickCollapseFilter()
      }
    },
    rangeSliderMarks() {
      const marks = {}
      for (let i = 0; i < 30; i += 5) {
        marks[i] = i.toString()
      }
      marks[30] = '30+'
      return marks
    },
  },
}
</script>
<style lang="scss" scoped>
#site-logo {
  width: 26px;
  vertical-align: bottom;
  margin-right: 5px;
}

#filter {
  @apply absolute w-full;
  transition: top 0.5s;
  box-shadow: 0 0 7px rgba(0, 0, 0, 0.5);

  @screen md {
    /* on large screen the event pane is attached to the top */
    @apply relative;
    max-width: 500px;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
