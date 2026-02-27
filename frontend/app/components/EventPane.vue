<template>
  <div
    v-if="!isClosed && store.pickedLocationData"
    id="event-pane-container"
    ref="containerEl"
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
        <div
          id="overlay"
          @pointerup="slideUp"
        />
        <div class="p-2 lg:p-6 absolute text-center text-white w-full">
          <span
            v-if="useDevice().isMobile()"
            @pointerup="slideUp"
          >
            <FontAwesomeIcon icon="grip-lines" size="lg" />
          </span>
        </div>
        <div class="p-2 lg:p-6 absolute right-0 text-white">
          <CloseButton :is-static="true" @collapse="close" />
        </div>
        <div class="p-2 lg:p-6">
          <h2
            class="text-3xl font-bold text-white absolute"
            style="bottom: 5px"
          >
            <span v-if="store.pickedLocationData.location.waterName"
              >{{ store.pickedLocationData.location.waterName }},
            </span>
            {{ store.pickedLocationData.location.city }},
            {{ store.pickedLocationData.location.country }}
            <div v-if="store.mylocation.isAccurate" class="text-base">
              {{ t('travelTime') }}:
              {{
                getFormattedTravelDistance(
                  store.pickedLocationData.location,
                  'DRIVING'
                )
              }}
              <a
                class="text-blue-300"
                :href="getDirectionsUrl(store.pickedLocationData.location)"
                target="_blank"
              >
                {{ t('directions') }}
              </a>
            </div>
          </h2>
        </div>
      </div>
      <!-- List of dates -->
      <div class="p-3 lg:p-6 lg:pb-2">
        <ul v-if="store.pickedLocationData.allEvents.edges.length > 1" class="tabs">
          <li
            v-for="(event, ix) in store.pickedLocationData.allEvents.edges"
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
            <FontAwesomeIcon icon="external-link-square-alt" />
          </a>
          <span v-else>{{ pickedEvent.node.name }}</span>
          <a
            v-if="pickedEvent.node.flyerImage"
            class="event-icon"
            @click="showFlyer"
          >
            <FontAwesomeIcon icon="image" />
          </a>
          <a class="event-icon" @click="zoomToEvent">
            <FontAwesomeIcon icon="search" />
          </a>
          <a
            v-if="authStore.loggedIn"
            class="event-icon"
            :href="getAdminEditUrl(pickedEvent.node.id)"
            target="_blank"
            @click="trackAdminEdit"
          >
            <FontAwesomeIcon icon="edit" />
            <span class="ml-1">Admin</span>
          </a>
        </h3>
        <div class="cursor-pointer inline-block pb-1" @click="showReviews()">
          <Reviews :event="pickedEvent.node" flavor="summary" />
        </div>
        <vue-easy-lightbox
          v-if="pickedEvent.node.flyerImage"
          :visible="showLightbox"
          :imgs="pickedEvent.node.flyerImage"
          @hide="showLightbox = false"
        />

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
              <FontAwesomeIcon icon="question-circle" />
            </span>
          </span>
          <div id="pickedEvent-textprops" class="flex my-2">
            <div v-if="pickedEvent.node.organizer" class="textprop flex-1">
              <div
                v-if="!pickedEvent.node.organizer.logo || useDevice().isMobile()"
                class="textprop-label"
              >
                {{ t('organizer') }}
              </div>
              <a
                v-if="pickedEvent.node.organizer.website"
                :href="pickedEvent.node.organizer.website"
                target="_blank"
              >
                <div
                  v-if="pickedEvent.node.organizer.logo && !useDevice().isMobile()"
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
              <div class="textprop-label">{{ t('waterType') }}</div>
              <div class="textprop-text">
                {{
                  store.pickedLocationData.location.waterType[0] +
                  store.pickedLocationData.location.waterType.slice(1).toLowerCase()
                }}
              </div>
            </div>
            <div v-if="pickedEvent.node.waterTemp" class="textprop flex-1">
              <div class="textprop-label">{{ t('waterTemperature') }}</div>
              <div class="textprop-text">{{ pickedEvent.node.waterTemp }}deg</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="pickedEvent.node.description && !showsReviews"
      class="scrollable px-3 lg:px-6"
    >
      <div>
        <div id="description">
          <div class="mb-2 whitespace-pre-line">
            <Translatable>{{ pickedEvent.node.description }}</Translatable>
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
              <th>{{ t('races') }}</th>
              <th></th>
              <th></th>
              <th>{{ t('wetsuit') }}</th>
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
                    {{ t('wetsuit' + race.node.wetsuit.toLowerCase()) }}
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
                      active: race.node.id == store.raceTrackUnderEditId,
                    }"
                    @click="store.raceTrackUnderEditId = race.node.id"
                  >
                    <FontAwesomeIcon icon="edit" />
                  </button>
                  <button
                    v-if="race.node.coordinates"
                    :class="{
                      'edit-button': true,
                      active: race.node.id == store.raceTrackUnderFocusId,
                    }"
                    @click="viewRaceDetail(race.node.id)"
                  >
                    <FontAwesomeIcon icon="search" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div v-if="showsReviews" class="scrollable px-3 lg:px-6">
      <Reviews
        flavor="expanded"
        :event="pickedEvent.node"
        @back="showsReviews = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const { t } = useI18n()
const store = useMainStore()
const authStore = useAuthStore()
const { gtag } = useGtag()
const config = useRuntimeConfig()

const {
  getBooleanProps,
  formatEventDate,
  formatRaceTime,
  humanizeDistance,
  getFormattedTravelDistance,
  getDirectionsUrl,
} = useEventPresentation()

const containerEl = ref(null)
const isClosed = ref(false)
const isSliddenUp = ref(false)
const showLightbox = ref(false)
const activeEventIndex = ref(0)
const eventPaneStyle = ref({})
const showsReviews = ref(false)

const pickedEvent = computed(() => {
  return store.pickedLocationData.allEvents.edges[activeEventIndex.value]
})

const headerPhotoUrl = computed(() => {
  return (
    store.pickedLocationData.location.headerPhoto ??
    config.public.defaultHeaderPhotoUrl
  )
})

watch(
  () => store.pickedLocationId,
  () => {
    isClosed.value = false
    activeEventIndex.value = 0
    showsReviews.value = false
    window.setTimeout(() => updateEventPaneStyle(), 100)
  }
)

watch(activeEventIndex, () => {
  store.focusedEventId = pickedEvent.value.node
  window.setTimeout(() => updateEventPaneStyle(), 100)
})

watch(
  () => store.raceTrackUnderFocusId,
  () => {
    isSliddenUp.value = false
    window.setTimeout(() => updateEventPaneStyle(), 100)
  }
)

onMounted(() => {
  updateEventPaneStyle()
  window.setTimeout(() => {
    updateEventPaneStyle()
  }, 1000)
})

function updateEventPaneStyle() {
  if (!containerEl.value) return
  const device = useDevice()
  if (device.isMobile()) {
    if (isSliddenUp.value) {
      eventPaneStyle.value = {
        top: window.innerHeight - containerEl.value.clientHeight + 'px',
      }
    } else {
      const height = device.isSmall() ? 120 : 160
      eventPaneStyle.value = {
        top: window.innerHeight - height + 'px',
      }
    }
  } else {
    eventPaneStyle.value = {
      maxHeight:
        (window.innerHeight - containerEl.value.offsetTop - 20).toString() +
        'px',
    }
  }
}

function close() {
  isClosed.value = true
  isSliddenUp.value = false
  updateEventPaneStyle()
}

function slideUp() {
  isSliddenUp.value = true
  updateEventPaneStyle()
}

function showFlyer() {
  showLightbox.value = true
  gtag('event', 'showEventPaneLightbox')
}

function zoomToEvent() {
  store.pickedLocationZoomedIn = store.pickedLocationId
  gtag('event', 'zoomToEvent')
}

function viewRaceDetail(id) {
  store.raceTrackUnderFocusId = id
  gtag('event', 'viewRaceDetail', id)
}

function raceRowHover(id) {
  store.raceTrackUnderHoverId = id
}

function showReviews() {
  gtag('event', 'reviewsShow')
  showsReviews.value = true
}

function getAdminEditUrl(nodeId) {
  try {
    const idParts = atob(nodeId).split(':')
    const numericId = idParts.length > 1 ? idParts[1] : null
    return numericId ? `/admin/app/event/${numericId}/change/` : '#'
  } catch (e) {
    console.error('Error extracting ID:', e)
    return '#'
  }
}

function trackAdminEdit() {
  gtag('event', 'editEventInAdmin', {
    event_id: pickedEvent.value.node.id,
  })
}
</script>

<style lang="scss" scoped>
.has-tooltip {
  cursor: pointer;
}

#event-pane-container {
  @apply absolute w-full;
  transition: top 0.5s;

  display: flex;
  flex-direction: column;
  overflow: hidden;

  max-height: 80vh;

  @screen md {
    @apply relative;
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

  @screen sm {
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

  @screen sm {
    height: 160px;
  }
}

ul.tabs {
  li {
    @apply inline-block mr-2 border-b-2 pb-1 cursor-pointer;
  }

  li.active {
    @apply border-b-2 border-blue-600;
  }
}

.badge {
  @apply inline-block rounded bg-gray-400 text-gray-800 px-1 py-1 text-xs font-bold mr-1 mt-1 uppercase;
}

.high {
  @apply bg-red-300;
}

.medium {
  @apply bg-orange-300;
}

.low {
  @apply bg-green-300;
}

.event-icon {
  @apply cursor-pointer float-right ml-2;
}

.textprop {
  .textprop-label {
    @apply font-bold;
  }
}

#race-table {
  .edit-button {
    @apply rounded px-1 text-blue-600;

    &.active {
      @apply bg-blue-600 text-white;
    }
  }
}

table th {
  @apply text-left;
}

table tr {
  @apply cursor-pointer;

  &:hover {
    @apply bg-gray-400;
  }
}

table td {
  @apply border-b border-t border-gray-400 py-1 pr-2;
}
</style>
