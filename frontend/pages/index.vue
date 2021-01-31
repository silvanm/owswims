<template>
  <div>
    <WelcomeBox
      v-if="
        welcomeboxShown &&
        !this.$store.getters.pickedLocationId &&
        !this.isEmbedded
      "
      @hide="hideWelcomeBox()"
    ></WelcomeBox>
    <div
      v-if="organizerData && !pickedLocationId && !this.$device.isMobile()"
      class="p-4"
    >
      <OrganizerLogo
        :image="organizerData.logo"
        :url="organizerData.website"
      ></OrganizerLogo>
    </div>
    <div class="xl:m-4">
      <LoginBox
        v-if="loginboxShown && !$store.getters['auth/loggedIn']"
        @hide="doHideLogin"
      ></LoginBox>
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
      <FilterBox
        ref="filterbox"
        v-if="!this.isEmbedded"
        @showLogin="doShowLogin"
      ></FilterBox>
      <EventPane v-if="$store.getters.pickedLocationId"></EventPane>
    </div>
  </div>
</template>

<script>
import gql from 'graphql-tag'
import { addMonths, formatISO } from 'date-fns'
import 'assets/slider.css'
import 'assets/v-tooltip.css'
import Spinner from '@/components/Spinner'
import EventPane from '@/components/EventPane'
import FilterBox from '@/components/FilterBox'
import { mapGetters } from 'vuex'
import axios from 'axios'

const apiKey = process.env.googleMapsKey

export default {
  components: { FilterBox, EventPane, Spinner },
  apollo: {
    locationsFiltered: {
      query: gql`
        query(
          $keyword: String!
          $distanceFrom: Float!
          $distanceTo: Float!
          $dateFrom: Date!
          $dateTo: Date!
          $organizerSlug: String!
        ) {
          locationsFiltered(
            keyword: $keyword
            raceDistanceGte: $distanceFrom
            raceDistanceLte: $distanceTo
            dateFrom: $dateFrom
            dateTo: $dateTo
            organizerSlug: $organizerSlug
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
          organizerSlug: this.organizerData ? this.organizerData.slug : '',
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
      loginboxShown: false,
      welcomeboxShown: false,
    }
  },
  computed: {
    ...mapGetters([
      'keyword',
      'distanceRange',
      'dateRange',
      'isLoading',
      'pickedLocationId',
      'organizerData',
      'isEmbedded',
    ]),
  },
  async mounted() {
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

    if (typeof localStorage !== 'undefined') {
      if (
        !this.$device.isMobile() &&
        !localStorage.getItem('welcomeBoxHidden')
      ) {
        this.welcomeboxShown = true
      }
    }
  },
  methods: {
    locationPicked() {
      if (this.$refs.filterbox) {
        this.$refs.filterbox.collapse()
      }
    },
    doShowLogin() {
      this.loginboxShown = true
    },
    doHideLogin() {
      this.loginboxShown = false
    },
    hideWelcomeBox() {
      this.welcomeboxShown = false
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('welcomeBoxHidden', true)
      }
    },
  },
  head() {
    return {
      script: [
        {
          src: `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=drawing&v=beta`,
        },
      ],
    }
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
