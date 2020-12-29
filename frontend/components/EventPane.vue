<template>
  <div
    v-if="!isClosed"
    id="event-pane-container"
    class="bg-white lg:mt-4 relative"
    :style="eventPaneStyle"
  >
    <div v-if="pickedLocationData">
      <div
        id="event-pane-header"
        :style="{
          backgroundImage: `url(${headerPhotoUrl})`,
        }"
      >
        <div id="overlay" v-touch:swipe="slideHandler" @click="slideUp"></div>
        <div class="p-4 lg:p-6 absolute text-center text-white w-full">
          <span
            v-if="$device.isMobile()"
            v-touch:swipe="slideHandler"
            @click="slideUp"
          >
            <font-awesome-icon icon="grip-lines" size="lg" />
          </span>
        </div>
        <div class="p-4 lg:p-6 absolute right-0 text-white">
          <CloseButton @collapse="close"></CloseButton>
        </div>
        <div class="p-4 lg:p-6">
          <h2
            class="text-3xl font-bold text-white absolute bottom-0"
            style="bottom: 4px"
          >
            {{ pickedLocationData.location.city }},
            {{ pickedLocationData.location.country }}
            <div v-if="$store.getters.mylocation.isAccurate" class="text-base">
              Travel time:
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
                Directions
              </a>
            </div>
          </h2>
        </div>
      </div>
      <!-- Start Event -->
      <div class="p-4 lg:p-6">
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

        <h3 class="text-xl font-bold py-2">
          <a :href="pickedEvent.node.website" target="_blank">
            {{ pickedEvent.node.name }}
          </a>
        </h3>
        <div>
          <span
            v-for="prop in getBooleanProps(pickedEvent.node)"
            :key="prop.id"
            :class="'badge ' + prop.importance"
          >
            {{ prop.label }}
            <span v-if="prop.info" v-tooltip="prop.info">
              <font-awesome-icon icon="question-circle" />
            </span>
          </span>
          <div id="pickedEvent-textprops" class="grid gap-0 grid-cols-3 my-2">
            <div v-if="pickedEvent.node.organizer" class="textprop">
              <div class="textprop-label">Organizer</div>
              <a
                v-if="pickedEvent.node.organizer.website"
                :href="pickedEvent.node.organizer.website"
                target="_blank"
              >
                <div class="textprop-text">
                  {{ pickedEvent.node.organizer.name }}
                </div>
              </a>
              <div v-else class="textprop-text">
                {{ pickedEvent.node.organizer.name }}
              </div>
            </div>
            <div v-if="pickedEvent.node.waterType" class="textprop">
              <div class="textprop-label">Water type</div>
              <div class="textprop-text">
                {{
                  pickedEvent.node.waterType[0] +
                  pickedEvent.node.waterType.slice(1).toLowerCase()
                }}
              </div>
            </div>
            <div v-if="pickedEvent.node.waterTemp" class="textprop">
              <div class="textprop-label">Water temperature</div>
              <div class="textprop-text">{{ pickedEvent.node.waterTemp }}°</div>
            </div>
          </div>

          <div v-if="pickedEvent.node.description" id="description">
            <div class="font-bold">Description</div>
            <div class="mb-2">
              {{ pickedEvent.node.description }}
            </div>
          </div>
          <div class="font-bold">Races</div>
          <table class="min-w-full" style="max-height: 200px; overflow: scroll">
            <tbody>
              <tr
                v-for="race in pickedEvent.node.races.edges"
                :key="race.node.id"
              >
                <td>
                  {{ formatEventDate(race.node.date, true) }}
                  {{ race.node.raceTime }}
                </td>
                <td class="text-right">
                  {{ humanizeDistance(race.node.distance) }}
                </td>
                <td>{{ race.node.name }}</td>
                <td>
                  <span v-if="race.node.priceValue !== 'None'">
                    {{ race.node.priceValue }}{{ race.node.priceCurrency }}
                  </span>
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
      activeEventIndex: 0,
      eventPaneStyle: {},
    }
  },
  computed: {
    ...mapGetters(['pickedLocationId', 'pickedLocationData']),
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
  },
  mounted() {
    this.updateEventPaneStyle()
  },
  methods: {
    updateEventPaneStyle() {
      if (this.$device.isMobile()) {
        if (this.isSliddenUp) {
          this.eventPaneStyle = {
            top: window.innerHeight - this.$el.clientHeight + 'px',
          }
        } else {
          this.eventPaneStyle = {
            top: window.innerHeight - 160 + 'px', // height of the header
          }
        }
      } else {
        this.eventPaneStyle = {}
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
  },
}
</script>
<style lang="scss" scoped>
#event-pane-container {
  @apply absolute w-full;
  transition: top 0.5s;

  @screen lg {
    /* on large screen the event pane is attached to the top */
    @apply relative;
    max-width: 500px;
  }
}

#event-pane-header {
  position: relative;
  background-size: cover;
  background-position: center;
  height: 160px;
}

#overlay {
  position: absolute;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0),
    rgba(0, 0, 0, 0.5)
  );
  width: 100%;
  height: 160px;
}

ul.tabs {
  li {
    @apply inline-block mr-2 border-b-2 pb-1 cursor-pointer;
  }

  li.active {
    @apply border-b-2 border-blue-600;
  }
}

#description {
  max-height: 200px;
  overflow: scroll;

  @screen lg {
    max-height: auto;
    overflow: auto;
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

.textprop {
  div {
    /*@apply inline-block;*/
  }

  .textprop-label {
    @apply font-bold;
    /*width: 100px;*/
  }
}

table td {
  @apply border-b border-t border-gray-400 py-1 pr-2;
}
</style>
