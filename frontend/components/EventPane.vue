<template>
  <div class="bg-white mt-4 relative" v-if="!isClosed">
    <div v-if="pickedLocationData">
      <div
        id="event-pane-header"
        :style="{
          backgroundImage: `url(${pickedLocationData.location.headerPhoto})`,
        }"
      >
        <div id="overlay"></div>
        <h1 class="p-5 absolute right-0">
          <CloseButton @collapse="close"></CloseButton>
        </h1>
        <div class="p-4">
          <h2
            class="text-3xl font-bold text-white absolute bottom-0"
            style="bottom: 4px"
          >
            {{ pickedLocationData.location.city }},
            {{ pickedLocationData.location.country }}
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
            <h3 class="text-xl font-bold">{{ event.node.name }}</h3>
            <div v-if="event.node.description">
              {{ event.node.description }}
            </div>
            <table>
              <tr v-for="race in event.node.races.edges" :key="race.node.id">
                <td>{{ formatEventDate(race.node.date, true) }}</td>
                <td>{{ humanizeDistance(race.node.distance) }}</td>
                <td>{{ race.node.name }}</td>
                <td v-if="race.node.priceValue !== 'None'">
                  {{ race.node.priceValue }}{{ race.node.priceCurrency }}
                </td>
              </tr>
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
    }
  },
  watch: {
    pickedLocationId(newVal, oldVal) {
      this.isClosed = false
    },
  },
  computed: {
    ...mapGetters(['pickedLocationId', 'pickedLocationData']),
  },
  methods: {
    close() {
      this.isClosed = true
    },
  },
}
</script>
<style lang="scss" scoped>
#event-pane-header {
  position: relative;
  background-size: cover;
  background-position: center;
  height: 160px;
}

#overlay {
  position: absolute;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.5));
  width: 100%;
  height: 160px;
}
</style>
