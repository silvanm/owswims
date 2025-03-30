<!--suppress ALL -->
<template>
  <div
    v-if="!isClosed && pickedLocationData"
    id="event-pane-container"
    class="bg-white xl:mt-4 relative"
    :style="eventPaneStyle"
  >
    <div class="not-scrollable">
      <div
        id="event-pane-header"
        :style="{
          backgroundImage: `url(${headerPhotoUrl})`,
        }"
      >
        <div id="overlay" v-touch:swipe="slideHandler" @click="slideUp"></div>
        <div class="p-2 lg:p-6 absolute text-center text-white w-full">
          <span
            v-if="isMobile"
            v-touch:swipe="slideHandler"
            @click="slideUp"
          >
            <font-awesome-icon icon="grip-lines" size="lg" />
          </span>
        </div>
        <div class="p-2 lg:p-6 absolute right-0 text-white">
          <CloseButton :is-static="true" @collapse="close"></CloseButton>
        </div>
        <div class="p-2 lg:p-6">
          <h2
            class="text-3xl font-bold text-white absolute"
            style="bottom: 5px"
          >
            <span v-if="pickedLocationData.location.waterName"
              >{{ pickedLocationData.location.waterName }},
            </span>
            {{ pickedLocationData.location.city }},
            {{ pickedLocationData.location.country }}
            <div v-if="mainStore.mylocation.isAccurate" class="text-base">
              {{ $t('travelTime') }}:
              {{
                getFormattedTravelDistance(
                  pickedLocationData.location,
                  'DRIVING'
                )
              }}
              <a
                class="text-blue-300"
                :href="getDirectionsUrl(pickedLocationData.location)"
                target="_blank"
              >
                {{ $t('directions') }}
              </a>
            </div>
          </h2>
        </div>
      </div>
      <!-- List of dates -->
      <div class="p-3 lg:p-6 lg:pb-2">
        <ul v-if="pickedLocationData.allEvents.edges.length > 1" class="tabs">
          <li
            v-for="(event, ix) in pickedLocationData.allEvents.edges"
            :key="event.node.id"
            :class="{
              active: activeEventIndex === ix,
            }"
          >
            <span @click="activeEventIndex = ix">{{
              formatEventDate(event.node.dateStart, false, 'd. MMM yyyy')
            }}</span>
          </li>
        </ul>
        <ul v-else>
          <li :class="{ 'inline-block': true, 'p-0': true }">
            <span>{{ formatEventDate(pickedEvent.node.dateStart) }}</span>
          </li>
        </ul>

        <!-- Single event -->
        <h3 class="text-xl font-bold pt-2">
          <a
            v-if="pickedEvent.node.website"
            :href="pickedEvent.node.website"
            target="_blank"
          >
            {{ pickedEvent.node.name }}
            <font-awesome-icon
              icon="external-link-square-alt"
            ></font-awesome-icon>
          </a>
          <span v-else>{{ pickedEvent.node.name }}</span>
          <a
            v-if="pickedEvent.node.flyerImage"
            class="event-icon"
            @click="showFlyer"
          >
            <font-awesome-icon icon="image"></font-awesome-icon>
          </a>
          <a class="event-icon" @click="zoomToEvent">
            <font-awesome-icon icon="search" />
          </a>
          <a
            v-if="authStore.loggedIn"
            class="event-icon"
            :href="getAdminEditUrl(pickedEvent.node.id)"
            target="_blank"
            @click="trackAdminEdit"
          >
            <font-awesome-icon icon="edit" />
            <span class="ml-1">Admin</span>
          </a>
        </h3>
        <div class="cursor-pointer inline-block pb-1" @click="showReviews()">
          <!-- Placeholder for Reviews component -->
          <div>Reviews Summary</div>
        </div>
        <!-- Placeholder for vue-easy-lightbox -->
        <div v-if="showLightbox" @click="showLightbox = false">
          Lightbox: {{ pickedEvent.node.flyerImage }}
        </div>

        <!-- Switch between Ratings and Event details -->
        <div v-if="!showsReviews">
          <span
            v-for="prop in getBooleanProps(pickedEvent.node)"
            :key="prop.id"
            :class="'badge ' + prop.importance"
          >
            {{ prop.label }}
            <span
              v-if="prop.info"
              v-tooltip="{ content: prop.info, trigger: 'click' }"
            >
              <font-awesome-icon icon="question-circle" />
            </span>
          </span>
          <div id="pickedEvent-textprops" class="flex my-2">
            <div v-if="pickedEvent.node.organizer" class="textprop flex-1">
              <div
                v-if="!pickedEvent.node.organizer.logo || isMobile"
                class="textprop-label"
                @load="updateEventPaneStyle"
              >
                {{ $t('organizer') }}
              </div>
              <a
                v-if="pickedEvent.node.organizer.website"
                :href="pickedEvent.node.organizer.website"
                target="_blank"
              >
                <div
                  v-if="pickedEvent.node.organizer.logo && !isMobile"
                  class="textprop-text"
                >
                  <img
                    :src="pickedEvent.node.organizer.logo"
                    style="max-width: 200px; max-height: 100px"
                  />
                </div>
                <div v-else class="textprop-text">
                  {{ pickedEvent.node.organizer.name }}
                </div>
              </a>
              <div v-else class="textprop-text">
                <div
                  v-if="pickedEvent.node.organizer.logo"
                  class="textprop-text"
                >
                  <img
                    :src="pickedEvent.node.organizer.logo"
                    style="width: 200px"
                  />
                </div>
                <div v-else class="textprop-text">
                  {{ pickedEvent.node.organizer.name }}
                </div>
              </div>
            </div>
            <div v-if="pickedEvent.node.waterType" class="textprop flex-1">
              <div class="textprop-label">{{ $t('waterType') }}</div>
              <div class="textprop-text">
                {{
                  pickedLocationData.node.waterType[0] +
                  pickedLocationData.node.waterType.slice(1).toLowerCase()
                }}
              </div>
            </div>
            <div v-if="pickedEvent.node.waterTemp" class="textprop flex-1">
              <div class="textprop-label">{{ $t('waterTemperature') }}</div>
              <div class="textprop-text">{{ pickedEvent.node.waterTemp }}°</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="pickedEvent.node.description && !showsReviews"
      class="scrollable px-3 lg:px-6"
      style=""
    >
      <div>
        <div id="description">
          <!-- prettier-ignore -->
          <div class="mb-2 whitespace-pre-line">
            <!-- Placeholder for Translatable component -->
            <div>{{ pickedEvent.node.description }}</div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="!showsReviews" class="scrollable px-3 lg:px-6">
      <div>
        <!-- Race table -->
        <div id="race-table">
            <table class="min-w-full">
              <thead>
                <tr>
                  <th>{{ $t('races') }}</th>
                  <th></th>
                  <th></th>
                  <th>{{ $t('wetsuit') }}</th>
                </tr>
              </thead>
            <tbody>
              <tr
                v-for="race in pickedEvent.node.races.edges"
                :key="race.node.id"
                @click="raceRowHover(race.node.id)"
                @mouseout="raceRowHover(null)"
                @mouseover="raceRowHover(race.node.id)"
              >
                <td>
                  {{ formatEventDate(race.node.date, true) }}
                  <span v-if="race.node.raceTime">
                    {{ formatRaceTime(race.node.raceTime) }}
                  </span>
                </td>
                <td class="text-right">
                  {{ humanizeDistance(race.node.distance) }}
                </td>
                <td>{{ race.node.name }}</td>
                <td>
                  <span v-if="race.node.wetsuit" class="badge">
                    {{ $t('wetsuit' + race.node.wetsuit.toLowerCase()) }}
                  </span>
                </td>
                <td class="text-right">
                  <span v-if="race.node.priceValue !== 'None'">
                    {{ race.node.priceValue }}{{ race.node.priceCurrency }}
                  </span>
                </td>
                <td>
                  <button
                    v-if="authStore.loggedIn"
                    :class="{
                      'edit-button': true,
                      active:
                        race.node.id == mainStore.raceTrackUnderEditId,
                    }"
                    @click="mainStore.raceTrackUnderEditId = race.node.id"
                  >
                    <font-awesome-icon icon="edit" />
                  </button>
                  <button
                    v-if="race.node.coordinates"
                    :class="{
                      'edit-button': true,
                      active:
                        race.node.id == mainStore.raceTrackUnderFocusId,
                    }"
                    @click="viewRaceDetail(race.node.id)"
                  >
                    <font-awesome-icon icon="search" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div v-if="showsReviews" class="scrollable px-3 lg:px-6">
      <!-- Placeholder for Reviews component -->
      <div>
        <button @click="showsReviews = false">Back</button>
        <div>Reviews Expanded</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useMainStore } from '@/stores/main'
import { useAuthStore } from '@/stores/auth'
import { format } from 'date-fns'
import { localeMap } from '@/constants'
import CloseButton from './CloseButton.vue'

// Define emits
defineEmits(['update'])

// Setup Apollo query (simplified for test project)
// In a real implementation, we would use useQuery from @vue/apollo-composable
// Apollo-related code is commented out for the test project
// const location = ref(null)
// const isLoading = ref(false)

// Define reactive state
const isClosed = ref(false)
const isSliddenUp = ref(false)
const showLightbox = ref(false)
const activeEventIndex = ref(0)
const eventPaneStyle = ref({})
const showsReviews = ref(false)

// Use Pinia stores
const mainStore = useMainStore()
const authStore = useAuthStore()

// Computed properties
const pickedLocationId = computed(() => mainStore.pickedLocationId)
const pickedLocationData = computed(() => mainStore.pickedLocationData)
const raceTrackUnderFocusId = computed(() => mainStore.raceTrackUnderFocusId)
const pickedEvent = computed(() => pickedLocationData.value.allEvents.edges[activeEventIndex.value])
const headerPhotoUrl = computed(() => 
  pickedLocationData.value.location.headerPhoto ?? 'https://example.com/default-header.jpg'
)
// Simplified device detection for test
const isMobile = computed(() => window.innerWidth < 768)

// Event presentation methods
const getBooleanProps = (event) => {
  const propNames = [
    {
      field: 'soldOut',
      labelTrue: 'Sold Out',
      importanceTrue: 'high',
    },
    {
      field: 'cancelled',
      labelTrue: 'Cancelled',
      importanceTrue: 'high',
    },
    {
      field: 'needsMedicalCertificate',
      labelTrue: 'Needs Medical Certificate',
      labelFalse: 'No Medical Certificate Required',
      importanceTrue: 'medium',
      importanceFalse: 'low',
      infoTrue: 'Medical certificate information',
    },
    {
      field: 'needsLicense',
      labelTrue: 'License Required',
      importanceTrue: 'medium',
    },
    {
      field: 'withRanking',
      labelFalse: 'No Ranking',
      importanceFalse: 'low',
    },
  ]

  return propNames
    .map((o) => {
      const r = {}
      r.id = o.field
      r.state = event[o.field]
      if (r.state === true) {
        r.label = o.labelTrue
        r.importance = o.importanceTrue
        r.info = o.infoTrue ?? false
      }
      if (r.state === false) {
        r.label = o.labelFalse
        r.importance = o.importanceFalse
        r.info = o.infoFalse ?? false
      }
      return r
    })
    .filter((o) => o.label)
}

const formatEventDate = (dt, short, custom = null) => {
  const capitalize = (s) => {
    if (typeof s !== 'string') return ''
    return s.charAt(0).toUpperCase() + s.slice(1)
  }

  let fmt
  if (custom) {
    fmt = custom
  } else if (short) {
    fmt = 'E d. MMM.'
  } else {
    fmt = 'EEEE, d. MMMM yyyy'
  }

  return capitalize(
    format(new Date(dt), fmt, { locale: localeMap['en'] })
  )
}

const formatRaceTime = (tm) => {
  if (!tm) {
    return ''
  } else {
    return format(new Date('2020-01-01 ' + tm), 'kk:mm')
  }
}

const humanizeDistance = (d) => {
  if (d <= 1.5) {
    return (d * 1000).toFixed(0) + 'm'
  } else {
    return d.toFixed(1) + 'km'
  }
}

const getFormattedTravelDistance = (_location, _travelMode) => {
  // Simplified implementation for test
  return '30 min (25km)'
}

const getDirectionsUrl = (location, _travelMode) => {
  // Simplified implementation for test
  return `https://www.google.com/maps/dir/?api=1&destination=${location.lat},${location.lng}`
}

// Methods
const updateEventPaneStyle = () => {
  if (isMobile.value) {
    if (isSliddenUp.value) {
      eventPaneStyle.value = {
        top: window.innerHeight - document.getElementById('event-pane-container').clientHeight + 'px',
      }
    } else {
      let height
      if (window.innerWidth < 640) {
        height = 120
      } else {
        height = 160
      }
      eventPaneStyle.value = {
        top: window.innerHeight - height + 'px', // height of the header
      }
    }
  } else {
    const el = document.getElementById('event-pane-container')
    if (el) {
      eventPaneStyle.value = {
        maxHeight: (window.innerHeight - el.offsetTop - 20).toString() + 'px',
      }
    }
  }
}

const close = () => {
  isClosed.value = true
  isSliddenUp.value = false
  updateEventPaneStyle()
}

const slideUp = () => {
  isSliddenUp.value = true
  updateEventPaneStyle()
}

// Keeping this method commented as it's not used but might be needed in the future
// const slideDown = () => {
//   isSliddenUp.value = false
//   updateEventPaneStyle()
// }

const slideHandler = (direction, e) => {
  // Replace $gtag with a placeholder for testing
  console.log('Event: eventPaneSlideHandler', direction)
  if (e) {
    e.preventDefault()
  }
  if (direction === 'top') {
    isSliddenUp.value = true
  } else if (direction === 'bottom') {
    isSliddenUp.value = false
  }
  updateEventPaneStyle()
}

const showFlyer = () => {
  showLightbox.value = true
  console.log('Event: showEventPaneLightbox')
}

const zoomToEvent = () => {
  mainStore.pickedLocationZoomedIn = pickedLocationId.value
  console.log('Event: zoomToEvent')
}

const viewRaceDetail = (id) => {
  mainStore.raceTrackUnderFocusId = id
  console.log('Event: viewRaceDetail', id)
}

const raceRowHover = (id) => {
  mainStore.raceTrackUnderHoverId = id
}

const showReviews = () => {
  console.log('Event: reviewsShow')
  showsReviews.value = true
}

const getAdminEditUrl = (nodeId) => {
  // Extract numeric ID from GraphQL node ID (format: "RXZlbnQ6MTIz" -> "123")
  try {
    const idParts = atob(nodeId).split(':')
    const numericId = idParts.length > 1 ? idParts[1] : null
    return numericId ? `/admin/app/event/${numericId}/change/` : '#'
  } catch (e) {
    console.error('Error extracting ID:', e)
    return '#'
  }
}

const trackAdminEdit = () => {
  console.log('Event: editEventInAdmin', {
    event_id: pickedEvent.value.node.id,
  })
}

// Helper method for translations in test environment
const $t = (key) => {
  const translations = {
    travelTime: 'Travel Time',
    directions: 'Directions',
    races: 'Races',
    wetsuit: 'Wetsuit',
    organizer: 'Organizer',
    waterType: 'Water Type',
    waterTemperature: 'Water Temperature',
    wetsuitrequired: 'Required',
    wetsuitoptional: 'Optional',
    wetsuitforbidden: 'Forbidden',
  }
  return translations[key] || key
}

// Watch for changes
watch(pickedLocationId, () => {
  isClosed.value = false
  activeEventIndex.value = 0
  showsReviews.value = false
  // this is ugly and needs to be fixed
  setTimeout(() => updateEventPaneStyle(), 100)
})

watch(activeEventIndex, () => {
  mainStore.focusedEventId = pickedEvent.value.node
  setTimeout(() => updateEventPaneStyle(), 100)
})

watch(raceTrackUnderFocusId, () => {
  // close the slider if someone wants to see a detail of a race
  isSliddenUp.value = false
  setTimeout(() => updateEventPaneStyle(), 100)
})

// Lifecycle hooks
onMounted(() => {
  updateEventPaneStyle()

  // @todo find out why this does not work if do it synchronously
  setTimeout(() => {
    updateEventPaneStyle()
  }, 1000)
})
</script>

<style scoped>
.has-tooltip {
  cursor: pointer;
}

#event-pane-container {
  position: absolute;
  width: 100%;
  transition: top 0.5s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-height: 80vh;
}

@media (min-width: 768px) {
  #event-pane-container {
    /* on large screen the event pane is attached to the top */
    position: relative;
    max-width: 500px;
    max-height: none;
  }
}

#event-pane-header {
  position: relative;
  background-size: cover;
  background-position: center;
  height: 120px;
  box-shadow: 0 0 7px rgba(0, 0, 0, 0.5);
}

@media (min-width: 640px) {
  #event-pane-header {
    height: 160px;
  }
}

.scrollable {
  overflow: scroll;
}

#overlay {
  position: absolute;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0),
    rgba(0, 0, 0, 0.5)
  );
  width: 100%;
  height: 120px;
}

@media (min-width: 640px) {
  #overlay {
    height: 160px;
  }
}

ul.tabs li {
  display: inline-block;
  margin-right: 0.5rem;
  border-bottom-width: 2px;
  padding-bottom: 0.25rem;
  cursor: pointer;
}

ul.tabs li.active {
  border-bottom-width: 2px;
  border-bottom-color: #3182ce;
}

.badge {
  display: inline-block;
  border-radius: 0.25rem;
  background-color: #cbd5e0;
  color: #2d3748;
  padding: 0.25rem;
  font-size: 0.75rem;
  font-weight: bold;
  margin-right: 0.25rem;
  margin-top: 0.25rem;
  text-transform: uppercase;
}

.high {
  background-color: #feb2b2;
}

.medium {
  background-color: #fbd38d;
}

.low {
  background-color: #9ae6b4;
}

.event-icon {
  cursor: pointer;
  float: right;
  margin-left: 0.5rem;
}

.textprop-label {
  font-weight: bold;
}

#race-table .edit-button {
  border-radius: 0.25rem;
  padding-left: 0.25rem;
  padding-right: 0.25rem;
  color: #3182ce;
}

#race-table .edit-button.active {
  background-color: #3182ce;
  color: white;
}

table th {
  text-align: left;
}

table tr {
  cursor: pointer;
}

table tr:hover {
  background-color: #cbd5e0;
}

table td {
  border-bottom-width: 1px;
  border-top-width: 1px;
  border-color: #cbd5e0;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
  padding-right: 0.5rem;
}
</style>
