<template>
  <div class="m-4" style="max-width: 500px">
    <client-only>
      <Map
        v-if="allLocations"
        ref="map"
        :google="google"
        :locations="allLocations.edges"
        :lat="lat"
        :lng="lng"
      />
    </client-only>
    <div class="bg-white p-4 relative">
      <h1 class="text-2xl font-semibold pb-4">Open-Water Swims DB</h1>
      <h2 class="font-semibold pl-6 pb-2">Distance</h2>
      <div class="pl-10 pr-10 pt-10 pb-5">
        <client-only>
          <vue-slider
            v-model="distanceRange"
            tooltip="always"
            dot-size="25"
            :min="0"
            :max="30"
          ></vue-slider>
        </client-only>
      </div>
      <h2 class="font-semibold pl-6 pb-2">Date</h2>
      <div class="pl-10 pr-10 pt-10">
        <DaterangeSlider @change="updateDateRange"></DaterangeSlider>
      </div>
      <button @click="locateMe">Locate me</button>
      <button @click="calculateDistances">Calculate Distances</button>
    </div>
  </div>
</template>

<script>
import gql from 'graphql-tag'
import { addMonths, formatISO } from 'date-fns'
import 'vue-slider-component/theme/antd.css'
import { Loader } from 'google-maps'

export default {
  apollo: {
    allLocations: {
      query: gql`
        query(
          $distanceFrom: Float!
          $distanceTo: Float!
          $dateFrom: Date!
          $dateTo: Date!
        ) {
          allLocations(
            raceDistanceGte: $distanceFrom
            raceDistanceLte: $distanceTo
            dateFrom: $dateFrom
            dateTo: $dateTo
          ) {
            edges {
              node {
                id
                country
                city
                lat
                lng
                events(dateStart_Gte: $dateFrom, dateEnd_Lte: $dateTo) {
                  edges {
                    node {
                      id
                      name
                      dateStart
                      dateEnd
                      website
                      races(
                        distance_Gte: $distanceFrom
                        distance_Lte: $distanceTo
                      ) {
                        edges {
                          node {
                            distance
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      `,
      variables() {
        return {
          distanceFrom: this.distanceRange[0],
          distanceTo: this.distanceRange[1],
          dateFrom: formatISO(addMonths(new Date(), this.dateRange[0]), {
            representation: 'date',
          }),
          dateTo: formatISO(addMonths(new Date(), this.dateRange[1]), {
            representation: 'date',
          }),
        }
      },
      debounce: 200,
    },
  },
  data() {
    return {
      google: null,
      distanceRange: [0, 30],
      // @todo: this must be applied to the slider
      dateRange: [-6, 12],
      lat: null,
      lng: null,
    }
  },
  async mounted() {
    const loader = new Loader('AIzaSyBJm1Vv5sZa0ZlRZ4-vxNSQQydMwXDPzZw', {})
    this.google = await loader.load()
    this.locateMe()
  },
  methods: {
    updateDateRange(range) {
      this.dateRange = range
    },
    locateMe() {
      navigator.geolocation.getCurrentPosition((position) => {
        this.lat = position.coords.latitude
        this.lng = position.coords.longitude
      })
    },
    calculateDistances() {
      this.$refs.map.calculateDistances()
    },
  },
}
</script>

<style></style>
