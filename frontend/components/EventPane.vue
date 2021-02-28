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
            v-if="$device.isMobile()"
            v-touch:swipe="slideHandler"
            @click="slideUp"
          >
            <font-awesome-icon icon="grip-lines" size="lg" />
          </span>
        </div>
        <div class="p-2 lg:p-6 absolute right-0 text-white">
          <CloseButton @collapse="close"></CloseButton>
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
            <div v-if="$store.getters.mylocation.isAccurate" class="text-base">
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
        <h3 class="text-xl font-bold py-2">
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
        </h3>
        <vue-easy-lightbox
          v-if="pickedEvent.node.flyerImage"
          :visible="showLightbox"
          :imgs="pickedEvent.node.flyerImage"
          @hide="showLightbox = false"
        ></vue-easy-lightbox>
        <div>
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
                v-if="!pickedEvent.node.organizer.logo"
                @load="updateEventPaneStyle"
                class="textprop-label"
              >
                {{ $t('organizer') }}
              </div>
              <a
                v-if="pickedEvent.node.organizer.website"
                :href="pickedEvent.node.organizer.website"
                target="_blank"
              >
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
              <div class="textprop-label">{{ $('waterType') }}</div>
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
    <div v-if="pickedEvent.node.description" class="scrollable px-2 lg:px-6">
      <div>
        <div id="description">
          <div class="mb-2">
            {{ pickedEvent.node.description }}
          </div>
        </div>
      </div>
    </div>
    <div class="scrollable px-2 lg:px-6">
      <div>
        <!-- Race table -->
        <div id="race-table">
          <table class="min-w-full">
            <thead>
              <th>{{ $t('races') }}</th>
              <th></th>
              <th></th>
              <th>{{ $t('wetsuit') }}</th>
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
                    {{ race.node.wetsuit }}
                  </span>
                </td>
                <td class="text-right">
                  <span v-if="race.node.priceValue !== 'None'">
                    {{ race.node.priceValue }}{{ race.node.priceCurrency }}
                  </span>
                </td>
                <td>
                  <button
                    v-if="$store.getters['auth/loggedIn']"
                    :class="{
                      'edit-button': true,
                      active:
                        race.node.id == $store.getters.raceTrackUnderEditId,
                    }"
                    @click="$store.commit('raceTrackUnderEditId', race.node.id)"
                  >
                    <font-awesome-icon icon="edit" />
                  </button>
                  <button
                    v-if="race.node.coordinates"
                    :class="{
                      'edit-button': true,
                      active:
                        race.node.id == $store.getters.raceTrackUnderFocusId,
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
  </div>
</template>
<script>
import { mapGetters } from 'vuex'
import gql from 'graphql-tag'
import eventPresentation from '@/mixins/eventPresentation'
import CloseButton from '@/components/CloseButton'

export default {
  components: { CloseButton },
  mixins: [eventPresentation],
  apollo: {
    location: {
      query: gql`
        query($locationId: ID!) {
          location(id: $locationId) {
            country
            city
            headerPhoto
          }
        }
      `,
      variables() {
        return {
          locationId: this.pickedLocationId,
        }
      },
      watchLoading(isLoading, countModifier) {
        this.isLoading = isLoading
      },
    },
  },
  data() {
    return {
      isClosed: false,
      isSliddenUp: false,
      showLightbox: false,
      activeEventIndex: 0,
      eventPaneStyle: {},
    }
  },
  computed: {
    ...mapGetters([
      'pickedLocationId',
      'pickedLocationData',
      'raceTrackUnderFocusId',
    ]),
    pickedEvent() {
      return this.pickedLocationData.allEvents.edges[this.activeEventIndex]
    },
    headerPhotoUrl() {
      return (
        this.pickedLocationData.location.headerPhoto ??
        process.env.defaultHeaderPhotoUrl
      )
    },
  },
  watch: {
    pickedLocationId(newVal, oldVal) {
      this.isClosed = false
      this.activeEventIndex = 0
      // this is ugly and needs to be fixed
      window.setTimeout(() => this.updateEventPaneStyle(), 100)
    },
    activeEventIndex(newVal, oldVal) {
      window.setTimeout(() => this.updateEventPaneStyle(), 100)
    },
    raceTrackUnderFocusId(newData, oldData) {
      // close the slider if someone wants to see a detail of a race
      this.isSliddenUp = false
      window.setTimeout(() => this.updateEventPaneStyle(), 100)
    },
  },
  mounted() {
    // @todo find out why this does not work if do it synchronously
    window.setTimeout(() => {
      this.updateEventPaneStyle()
    }, 500)
  },
  methods: {
    updateEventPaneStyle() {
      if (this.$device.isMobile()) {
        if (this.isSliddenUp) {
          this.eventPaneStyle = {
            top: window.innerHeight - this.$el.clientHeight + 'px',
          }
        } else {
          let height
          if (this.$device.isSmall()) {
            height = 120
          } else {
            height = 160
          }
          this.eventPaneStyle = {
            top: window.innerHeight - height + 'px', // height of the header
          }
        }
      } else {
        this.eventPaneStyle = {
          maxHeight:
            (window.innerHeight - this.$el.offsetTop - 20).toString() + 'px',
        }
      }
    },
    close() {
      this.isClosed = true
      this.isSliddenUp = false
      this.updateEventPaneStyle()
    },
    slideUp() {
      this.isSliddenUp = true
      this.updateEventPaneStyle()
    },
    slideDown() {
      this.isSliddenUp = false
      this.updateEventPaneStyle()
    },
    slideHandler(direction, e) {
      this.$gtag('event', 'eventPaneSlideHandler', direction)
      if (e) {
        e.preventDefault()
      }
      if (direction === 'top') {
        this.isSliddenUp = true
      } else if (direction === 'bottom') {
        this.isSliddenUp = false
      }
      this.updateEventPaneStyle()
    },
    showFlyer() {
      this.showLightbox = true
      this.$gtag('event', 'showEventPaneLightbox')
    },
    zoomToEvent() {
      this.$store.commit('pickedLocationZoomedIn', this.pickedLocationId)
    },
    viewRaceDetail(id) {
      this.$store.commit('raceTrackUnderFocusId', id)
    },
    raceRowHover(id) {
      this.$store.commit('raceTrackUnderHoverId', id)
    },
  },
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
    /* on large screen the event pane is attached to the top */
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
  div {
    /*@apply inline-block;*/
  }

  .textprop-label {
    @apply font-bold;
    /*width: 100px;*/
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
