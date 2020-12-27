<template>
  <div
    id="event-pane-container"
    class="bg-white lg:mt-4 relative"
    v-if="!isClosed"
    :style="eventPaneStyle"
  >
    <div v-if="pickedLocationData">
      <div
        id="event-pane-header"
        :style="{
          backgroundImage: `url(${headerPhotoUrl})`,
        }"
      >
        <div
          id="overlay"
          v-touch:swipe.prevent="slideHandler"
          @click="slideUp"
        ></div>
        <div class="p-4 lg:p-5 absolute text-center text-white w-full">
          <span
            v-if="$device.isMobile()"
            v-touch:swipe="slideHandler"
            @click="slideUp"
          >
            <font-awesome-icon icon="grip-lines" size="lg" />
          </span>
        </div>
        <div class="p-4 lg:p-5 absolute right-0 text-white">
          <CloseButton @collapse="close"></CloseButton>
        </div>
        <div class="p-4">
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
      <div class="p-4">
        <ul>
          <li
            v-for="event in pickedLocationData.allEvents.edges"
            :key="event.node.id"
          >
            {{ formatEventDate(event.node.dateStart) }}
            <h3 class="text-xl font-bold py-2">
              <a :href="event.node.website" target="_blank">
                {{ event.node.name }}
              </a>
            </h3>
            <div>
              <span
                v-for="prop in getBooleanProps(event.node)"
                :key="prop.id"
                :class="'badge ' + prop.importance"
              >
                {{ prop.label }}
                <span v-if="prop.info" v-tooltip="prop.info">
                  <font-awesome-icon icon="question-circle" />
                </span>
              </span>
            </div>
            <div id="event-textprops" class="grid gap-0 grid-cols-3 my-2">
              <div v-if="event.node.organizer" class="textprop">
                <div class="textprop-label">Organizer</div>
                <a
                  v-if="event.node.organizer.website"
                  :href="event.node.organizer.website"
                  target="_blank"
                >
                  <div class="textprop-text">
                    {{ event.node.organizer.name }}
                  </div>
                </a>
                <div v-else class="textprop-text">
                  {{ event.node.organizer.name }}
                </div>
              </div>
              <div v-if="event.node.waterType" class="textprop">
                <div class="textprop-label">Water type</div>
                <div class="textprop-text">
                  {{
                    event.node.waterType[0] +
                    event.node.waterType.slice(1).toLowerCase()
                  }}
                </div>
              </div>
              <div v-if="event.node.waterTemp" class="textprop">
                <div class="textprop-label">Water temperature</div>
                <div class="textprop-text">{{ event.node.waterTemp }}°</div>
              </div>
            </div>

            <div v-if="event.node.description" id="description">
              <div class="font-bold">Description</div>
              <div class="mb-2">
                {{ event.node.description }}
              </div>
            </div>
            <div class="font-bold">Races</div>
            <table class="min-w-full">
              <tbody>
                <tr v-for="race in event.node.races.edges" :key="race.node.id">
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
          </li>
        </ul>
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
    }
  },
  computed: {
    ...mapGetters(['pickedLocationId', 'pickedLocationData']),
    eventPaneStyle() {
      if (this.$device.isMobile()) {
        if (this.isSliddenUp) {
          return {
            top: window.innerHeight - this.$el.clientHeight + 'px',
          }
        } else {
          return {
            top: window.innerHeight - 160 + 'px', // height of the header
          }
        }
      } else {
        return {}
      }
    },
    headerPhotoUrl() {
      console.log(process.env.defaultHeaderPhotoUrl)
      return (
        this.pickedLocationData.location.headerPhoto ??
        process.env.defaultHeaderPhotoUrl
      )
    },
  },
  watch: {
    pickedLocationId(newVal, oldVal) {
      this.isClosed = false
    },
  },
  methods: {
    close() {
      this.isClosed = true
      this.isSliddenUp = false
    },
    slideUp() {
      console.log('slideUp')
      this.isSliddenUp = true
    },
    slideDown() {
      console.log('slideDown')
      this.isSliddenUp = false
    },
    slideHandler(direction) {
      if (direction === 'top') {
        this.isSliddenUp = true
      } else if (direction === 'bottom') {
        this.isSliddenUp = false
      }
    },
  },
}
</script>
<style lang="scss">
.fa-plus,
.fa-grip-lines {
  filter: drop-shadow(0px 0px 3px black);
}

#event-pane-container {
  @apply absolute w-full;
  transition: top 0.5s;

  @screen lg {
    /* on large screen the event pane is attached to the top */
    @apply relative;
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
