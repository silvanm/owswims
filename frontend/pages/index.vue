<template>
  <div style="max-width: 600px">
    <client-only>
      <Map v-if="allLocations" :locations="allLocations.edges" />
    </client-only>
    <div class="bg-white rounded-md p-2 relative">
      <h2>Distance</h2>
      <div class="p-10">
        <client-only>
          <vue-slider
            tooltip="always"
            v-model="distanceRange"
            dotSize="25"
            :min="0"
            :max="30"
          ></vue-slider>
        </client-only>
      </div>
      <h2>Date</h2>
      <div class="p-10">
        <DaterangeSlider @change="updateDateRange"></DaterangeSlider>
      </div>
    </div>
  </div>
</template>

<script>
import gql from 'graphql-tag'
import { addDays, formatISO } from 'date-fns'

import 'vue-slider-component/theme/antd.css'
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
          dateFrom: formatISO(addDays(new Date(), this.dateRange[0]), {
            representation: 'date',
          }),
          dateTo: formatISO(addDays(new Date(), this.dateRange[1]), {
            representation: 'date',
          }),
        }
      },
      debounce: 200,
    },
  },
  data() {
    return {
      distanceRange: [0, 30],
      dateRange: [-6 * 30, 12 * 30],
    }
  },
  methods: {
    updateDateRange(range) {
      console.log(range)
      this.dateRange = range
    },
  },
}
</script>

<style></style>
