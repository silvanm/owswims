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
    <div class="bg-white p-6 relative">
      <h1 class="text-2xl font-semibold pb-4 text-primary">
        🏊🏻‍️ European Open-Water Events
      </h1>
      <h2 class="font-semibold pb-2">Distance</h2>
      <div class="pl-4 pr-4 pb-5">
        <client-only>
          <vue-slider
            v-model="distanceRange"
            :marks="(val) => val % 5 === 0"
            :tooltip-formatter="(val) => `${val}km`"
            dot-size="25"
            :min="0"
            :max="30"
          ></vue-slider>
        </client-only>
      </div>
      <h2 class="font-semibold pb-2">Date</h2>
      <div class="pl-4 pr-4 pb-8">
        <DaterangeSlider @change="updateDateRange"></DaterangeSlider>
      </div>
      <Toggle
        name="locateMe"
        @change="(e) => (e ? locateMe() : null)"
        :is-checked="geoLocationEnabled"
        >Display Travel times</Toggle
      >
    </div>
  </div>
</template>

<script>
import gql from 'graphql-tag'
import { addMonths, formatISO } from 'date-fns'
import 'assets/slider.css'
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
      geoLocationEnabled: false,
    }
  },
  async mounted() {
    const loader = new Loader(process.env.googleMapsKey, {})
    this.google = await loader.load()
  },

  methods: {
    updateDateRange(range) {
      this.dateRange = range
    },
    locateMe() {
      console.log('Locating me')
      const store = this.$store
      navigator.geolocation.getCurrentPosition(
        (position) => {
          console.log(
            `storing position lat=${position.coords.latitude}, lng=${position.coords.longitude}`
          )
          store.commit('mylocation', {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          })
        },
        () => {
          console.log('Geolocation has failed')
        }
      )
    },
  },
}
</script>

<style></style>
