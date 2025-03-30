<!--suppress ALL -->
<template>
  <div id="filter">
    <!-- pb-3 is a hack because the div which can collapse always has a height of 2 -->
    <div class="bg-white p-4 pb-2 lg:p-6 lg:pb-5 relative overflow-hidden">
      <h1 class="text-l md:text-2xl font-semibold text-primary">
        ‍️<a href="/" style="color: black; text-decoration: none">
          <img
            id="site-logo"
            class="inline"
            src="https://example.com/site_logo.svg"
            alt="Site Logo"
          />
          open-water-swims.com</a
        >
        <div class="inline float-right text-gray-600">
          <span class="text-base">
            <span
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
            <span class="pr-2 cursor-pointer" @click="clickEnvelope">
              <font-awesome-icon icon="envelope" size="lg"></font-awesome-icon>
            </span>
            <span class="text-black">
              <CloseButton
                ref="closebutton"
                @collapse="clickCollapseFilter"
                @expand="filterCollapsed = false"
              ></CloseButton>
            </span>
          </span>
        </div>
      </h1>
      <!-- Tagline -->
      <h2
        class="mt-1 overflow-hidden"
        :style="{
          maxHeight: (isDisplayTagline() ? 200 : 0) + 'px',
          transition: 'max-height 0.5s',
        }"
      >
        {{ $t('tagline') }}
      </h2>

      <div
        style="transition: max-height 0.5s linear"
        :style="{
          maxHeight: filterCollapsed && !expandedPane ? 0 : '800px',
        }"
      >
        <div
          id="infos"
          class="overflow-hidden mt-0"
          style="transition: max-height 0.5s linear"
          :style="{
            maxHeight: expandedPane === 'info' ? '500px' : 0,
          }"
        >
          <!-- Placeholder for InfoTab component -->
          <div class="p-4 bg-gray-100">
            <h3 class="font-bold text-lg mb-2">Information</h3>
            <p>This is a placeholder for the InfoTab component.</p>
            <button 
              class="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              @click="$emit('showLogin')"
            >
              Login
            </button>
          </div>
        </div>
        <!-- Keyword search -->
        <div
          id="optional-search-params"
          style="transition: max-height 0.5s linear"
          :style="{
            maxHeight: expandedPane === 'search' ? '500px' : 0,
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
            <!-- Placeholder for OrganizerSelector component -->
            <div class="p-2 bg-gray-100">
              <p>Organizer Selector Placeholder</p>
            </div>
          </label>
        </div>
        <!-- Contact -->
        <div
          id="contact"
          style="transition: max-height 0.5s linear"
          :style="{
            maxHeight: expandedPane === 'contact' ? '500px' : 0,
          }"
          class="overflow-hidden"
        >
          <!-- Placeholder for ContactForm component -->
          <div class="p-4 bg-gray-100">
            <h3 class="font-bold text-lg mb-2">Contact Form</h3>
            <p>This is a placeholder for the ContactForm component.</p>
            <button 
              class="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              @click="expandedPane = null"
            >
              Send (Simulated)
            </button>
          </div>
        </div>
        <!-- Search by other parameters -->
        <h2 class="font-semibold pb-2 pt-3 lg:pt-4">
          {{ $t('raceDistance') }}
        </h2>
        <div id="race-distance-slider" class="pl-4 pr-4 pb-5">
          <client-only>
            <!-- Using @vueform/slider instead of vue-slider-component -->
            <Slider
              v-model="distanceRange"
              :marks="rangeSliderMarks()"
              :tooltip-formatter="(val) => `${val}km`"
              :dot-size="25"
              :min="0"
              :max="30"
            />
          </client-only>
        </div>
        <h2 class="font-semibold pb-2">
          {{ $t('date') }}
          <span
            :class="{
              'ml-1': true,
              'cursor-pointer': true,
              'text-blue-600': showCalendar,
              'text-blue-300': !showCalendar,
            }"
            @click="toggleCalendar()"
          >
            <font-awesome-icon :icon="['far', 'calendar']"></font-awesome-icon>
          </span>
        </h2>
        <div id="date-range-slider">
          <DaterangeSlider
            :show-calendar="showCalendar"
            @change="updateDateRange"
          ></DaterangeSlider>
        </div>
        <Toggle
          name="locateMe"
          :is-checked="geoLocationEnabled"
          @change="handleGeoLocationChange"
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
import { ref, computed, watch } from 'vue'
import { useMainStore } from '@/stores/main'
import Slider from '@vueform/slider'
import CloseButton from './CloseButton.vue'
import DaterangeSlider from './DaterangeSlider.vue'
import Toggle from './Toggle.vue'

const distanceRangeMax = 30

export default {
  name: 'FilterBox',
  components: { 
    CloseButton, 
    DaterangeSlider, 
    Toggle,
    Slider
  },
  // Add explicit emits declaration
  emits: ['showLogin'],
  setup() {
    const mainStore = useMainStore()
    
    // State
    const expandedPane = ref(null)
    const keyword = ref('')
    const distanceRange = ref([0, distanceRangeMax])
    const dateRange = ref(null)
    const geoLocationEnabled = ref(false)
    const filterCollapsed = ref(false)
    const showCalendar = ref(false)
    const closebutton = ref(null)

    // Computed
    const isMobile = computed(() => {
      return window.innerWidth < 768
    })

    // Methods
    const toggleCalendar = () => {
      showCalendar.value = !showCalendar.value
      console.log('Event: toggleCalendar')
    }

    const isDisplayTagline = () => {
      if (filterCollapsed.value) {
        return false
      }
      if (isMobile.value) {
        return mainStore.justMounted
      }
      return true
    }

    const clickCollapseFilter = () => {
      console.log('Event: clickCollapseFilter')
      filterCollapsed.value = true
      expandedPane.value = null
    }

    const clickOptionalSearchParamsButton = () => {
      expandedPane.value = 'search'
      console.log('Event: clickOptionalSearchParamsButton')
      if (expandedPane.value === 'search') {
        keyword.value = ''
      }
    }

    const clickEnvelope = () => {
      expandedPane.value = 'contact'
      console.log('Event: clickEnvelope')
    }

    const clickInfoCircle = () => {
      expandedPane.value = 'info'
      console.log('Event: clickInfoCircle')
    }

    const updateDateRange = (range) => {
      dateRange.value = range
      mainStore.$patch({ dateRange: [range[0], range[1]] })
      console.log('Event: dateRange')
    }

    const collapse = () => {
      if (isMobile.value) {
        closebutton.value?.collapse()
        clickCollapseFilter()
      }
    }

    const rangeSliderMarks = () => {
      const marks = {}
      for (let i = 0; i < distanceRangeMax; i += 5) {
        marks[i] = i.toString()
      }
      marks[distanceRangeMax] = `${distanceRangeMax}+`
      return marks
    }

    const handleGeoLocationChange = (enabled) => {
      if (enabled) {
        mainStore.locateMe()
      }
      geoLocationEnabled.value = enabled
    }

    // Watchers
    watch(distanceRange, (newRange) => {
      // if the slider is at the upper edge, then don't have a limit
      const range = [...newRange]
      if (range[1] === distanceRangeMax) {
        range[1] = 1000
      }
      mainStore.$patch({ distanceRange: range })
      console.log('Event: distanceRange')
    })

    watch(keyword, (newKeyword) => {
      mainStore.$patch({ keyword: newKeyword })
      console.log('Event: keyword')
    })

    // Helper method for translations in test environment
    const $t = (key) => {
      const translations = {
        tagline: 'Find open water swimming events near you',
        keywordSearch: 'Keyword Search',
        keywordPlaceholder: 'Search for events, locations, or organizers',
        organizerSerie: 'Organizer / Series',
        raceDistance: 'Race Distance',
        date: 'Date',
        showTripDuration: 'Show Trip Duration',
        showTripDurationTooltip: 'Enable location services to see travel times to events',
      }
      return translations[key] || key
    }

    return {
      // State
      expandedPane,
      keyword,
      distanceRange,
      dateRange,
      geoLocationEnabled,
      filterCollapsed,
      showCalendar,
      closebutton,
      
      // Methods
      toggleCalendar,
      isDisplayTagline,
      clickCollapseFilter,
      clickOptionalSearchParamsButton,
      clickEnvelope,
      clickInfoCircle,
      updateDateRange,
      collapse,
      rangeSliderMarks,
      handleGeoLocationChange,
      
      // Helper
      $t
    }
  }
}
</script>

<style scoped>
#site-logo {
  width: 26px;
  vertical-align: middle;
  margin-right: 5px;
}

#filter {
  position: absolute;
  width: 100%;
  transition: top 0.5s;
  box-shadow: 0 0 7px rgba(0, 0, 0, 0.5);
}

@media (min-width: 768px) {
  #filter {
    /* on large screen the event pane is attached to the top */
    position: relative;
    max-width: 500px;
  }
}
</style>
