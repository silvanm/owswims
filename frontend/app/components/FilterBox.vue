<template>
  <div id="filter">
    <div class="bg-white p-4 pb-2 lg:p-6 lg:pb-5 relative overflow-hidden">
      <h1 class="text-l md:text-2xl font-semibold text-primary">
        <a href="/" style="color: black; text-decoration: none">
          <img
            id="site-logo"
            class="inline"
            src="~/assets/site_logo.svg"
          />
          open-water-swims.com</a
        >
        <div class="inline float-right text-gray-600">
          <span class="text-base">
            <span
              class="pr-2 cursor-pointer"
              @click="clickOptionalSearchParamsButton"
            >
              <FontAwesomeIcon icon="search" size="lg" />
            </span>
            <span class="pr-2 cursor-pointer" @click="clickInfoCircle">
              <FontAwesomeIcon icon="info-circle" size="lg" />
            </span>
            <span class="pr-2 cursor-pointer" @click="clickEnvelope">
              <FontAwesomeIcon icon="envelope" size="lg" />
            </span>
            <span class="text-black">
              <CloseButton
                ref="closebutton"
                @collapse="clickCollapseFilter"
                @expand="filterCollapsed = false"
              />
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
        {{ t('tagline') }}
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
          <InfoTab @show-login="emit('showLogin')" />
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
            <div class="pb-2">{{ t('keywordSearch') }}</div>
            <input
              id="keyword"
              v-model="keyword"
              type="text"
              :placeholder="t('keywordPlaceholder')"
              class="form-input block border p-2 w-full"
            />
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
          <ContactForm @mailsent="expandedPane = null" />
        </div>
        <!-- Search by other parameters -->
        <h2 class="font-semibold pb-2 pt-3 lg:pt-4">
          {{ t('raceDistance') }}
        </h2>
        <div id="race-distance-slider" class="pl-4 pr-4 pb-5">
          <ClientOnly>
            <VueSlider
              v-model="distanceRangeLocal"
              :marks="rangeSliderMarks()"
              :tooltip-formatter="(val) => `${val}km`"
              :dot-size="25"
              :min="0"
              :max="30"
            />
          </ClientOnly>
        </div>
        <h2 class="font-semibold pb-2">
          {{ t('date') }}
          <span
            :class="{
              'ml-1': true,
              'cursor-pointer': true,
              'text-blue-600': showCalendar,
              'text-blue-300': !showCalendar,
            }"
            @click="toggleCalendar()"
          >
            <FontAwesomeIcon :icon="['far', 'calendar']" />
          </span>
        </h2>
        <div id="date-range-slider">
          <DaterangeSlider
            :show-calendar="showCalendar"
            @change="updateDateRange"
          />
        </div>
        <Toggle
          name="locateMe"
          :is-checked="geoLocationEnabled"
          @change="(e) => (e ? store.locateMe() : null)"
        >
          <span id="activate-geolocation">{{ t('showTripDuration') }}</span>
          <span
            v-tooltip="{
              content: t('showTripDurationTooltip'),
              trigger: 'hover',
            }"
            class="text-gray-800 cursor-pointer"
          >
            <FontAwesomeIcon icon="question-circle" />
          </span>
        </Toggle>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import VueSlider from 'vue-slider-component'
import 'vue-slider-component/theme/default.css'

const { t } = useI18n()
const store = useMainStore()
const { gtag } = useGtag()

const emit = defineEmits(['showLogin'])

const distanceRangeMax = 30

const expandedPane = ref(null)
const keyword = ref('')
const distanceRangeLocal = ref([0, distanceRangeMax])
const dateRange = ref(null)
const geoLocationEnabled = ref(false)
const filterCollapsed = ref(false)
const showCalendar = ref(false)
const closebutton = ref(null)

const activeInfoTab = computed(() => store.activeInfoTab)

onMounted(() => {
  if (activeInfoTab.value) {
    expandedPane.value = 'info'
    filterCollapsed.value = false
  }
})

watch(activeInfoTab, (tab) => {
  if (tab) {
    expandedPane.value = 'info'
    filterCollapsed.value = false
  }
})

watch(expandedPane, (newPane, oldPane) => {
  if (oldPane === 'info' && newPane !== 'info') {
    store.activeInfoTab = null
    useUrlHistory().push({}, '/')
  }
})

watch(distanceRangeLocal, (newRange) => {
  const range = [...newRange]
  if (range[1] === distanceRangeMax) {
    range[1] = 1000
  }
  store.distanceRange = range
  gtag('event', 'distanceRange')
})

watch(keyword, (newKeyword) => {
  store.keyword = newKeyword
  gtag('event', 'keyword')
})

function toggleCalendar() {
  showCalendar.value = !showCalendar.value
  gtag('event', 'toggleCalendar')
}

function isDisplayTagline() {
  if (filterCollapsed.value) {
    return false
  }
  if (useDevice().isMobile()) {
    return store.justMounted
  }
  return true
}

function clickCollapseFilter() {
  gtag('event', 'clickCollapseFilter')
  filterCollapsed.value = true
  expandedPane.value = null
}

function clickOptionalSearchParamsButton() {
  expandedPane.value = 'search'
  gtag('event', 'clickOptionalSearchParamsButton')
}

function clickEnvelope() {
  filterCollapsed.value = false
  expandedPane.value = 'contact'
  gtag('event', 'clickEnvelope')
}

function clickInfoCircle() {
  expandedPane.value = 'info'
  store.activeInfoTab = 'help'
  useUrlHistory().push({}, '/info/help')
  gtag('event', 'clickInfoCircle')
}

function updateDateRange(range) {
  dateRange.value = range
  store.dateRange = [range[0], range[1]]
  gtag('event', 'dateRange')
}

function collapse() {
  if (useDevice().isMobile()) {
    closebutton.value?.collapse()
    clickCollapseFilter()
  }
}

function rangeSliderMarks() {
  const marks = {}
  for (let i = 0; i < distanceRangeMax; i += 5) {
    marks[i] = i.toString()
  }
  marks[distanceRangeMax] = `${distanceRangeMax}+`
  return marks
}

defineExpose({ collapse })
</script>

<style lang="scss" scoped>
#site-logo {
  width: 26px;
  vertical-align: middle;
  margin-right: 5px;
}

#filter {
  @apply absolute w-full;
  transition: top 0.5s;
  box-shadow: 0 0 7px rgba(0, 0, 0, 0.5);

  @screen md {
    @apply relative;
    max-width: 500px;
  }
}
</style>
