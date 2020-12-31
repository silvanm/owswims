<template>
  <div class="xl:m-4">
    <Tour></Tour>
    <client-only>
      <Map
        v-if="locationsFiltered"
        ref="map"
        :locations="locationsFiltered"
        :lat="lat"
        :lng="lng"
        :distance-from="distanceRange[0]"
        :distance-to="distanceRange[1]"
        :date-range="dateRange"
        @locationPicked="locationPicked()"
      />
    </client-only>
    <Spinner :show="isLoading"></Spinner>
    <FilterBox ref="filterbox"></FilterBox>
    <EventPane v-if="$store.getters.pickedLocationId"></EventPane>
  </div>
</template>

<script>
import gql from 'graphql-tag'
import { addMonths, formatISO } from 'date-fns'
import 'assets/slider.css'
import 'assets/v-tooltip.css'
import Spinner from '@/components/Spinner'
import Tour from '@/components/Tour'
import EventPane from '@/components/EventPane'
import FilterBox from '@/components/FilterBox'
import { mapGetters } from 'vuex'
import axios from 'axios'

export default {
  components: { FilterBox, EventPane, Spinner, Tour },
  apollo: {
    locationsFiltered: {
      query: gql`
        query(
          $keyword: String!
          $distanceFrom: Float!
          $distanceTo: Float!
          $dateFrom: Date!
          $dateTo: Date!
        ) {
          locationsFiltered(
            keyword: $keyword
            raceDistanceGte: $distanceFrom
            raceDistanceLte: $distanceTo
            dateFrom: $dateFrom
            dateTo: $dateTo
          ) {
            id
            country
            city
            lat
            lng
          }
        }
      `,
      variables() {
        return {
          keyword: this.keyword,
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
      lat: null,
      lng: null,
      geoLocationEnabled: false,
      filterCollapsed: false,
    }
  },
  computed: {
    ...mapGetters(['keyword', 'distanceRange', 'dateRange', 'isLoading']),
  },
  async mounted() {
    this.google = await this.$google()

    // detect coarse position via IP
    const response = await axios.post(
      'https://www.googleapis.com/geolocation/v1/geolocate?key=' +
        process.env.googleMapsKey,
      { considerIp: 'true' }
    )

    if (response.data.location) {
      this.$store.commit('mylocation', {
        isAccurate: false,
        latlng: response.data.location,
      })
    }
  },
  methods: {
    locationPicked() {
      this.$refs.filterbox.collapse()
    },
  },
}
</script>
<style lang="scss">
body {
  position: fixed;
}

a {
  @apply text-blue-600;
}

a:hover {
  @apply underline;
}
</style>
