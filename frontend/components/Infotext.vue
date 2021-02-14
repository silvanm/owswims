<template>
  <div>
    <div style="max-width: 600px" class="relative">
      <h1
        v-if="extended"
        class="text-xl md:text-2xl font-semibold text-primary"
      >
        Welcome to European Open-Water Swims
      </h1>
      <div class="absolute right-0 bottom-0">
        <button
          v-if="extended"
          class="bg-blue-600 rounded p-2 text-white font-bold float-right"
          @click="$emit('hide')"
        >
          Dismiss
        </button>
      </div>
      <p v-if="extended" class="font-semibold">
        <img
          class="inline float-right"
          :src="require('@/assets/silvan-muehlemann.jpg')"
          style="width: 100px; padding-left: 4px"
        />
        This is a not-for-profit project from open-water swimmers for open-water
        swimmers. We want to help you find your perfect swim events in Europe.
      </p>
      <p v-if="statistics">
        If you plan your vacations around open-water swim events, then this app
        is for you. Select the desired distance and time range, and out of
        <strong>{{ statistics.raceCount }}</strong> races in
        <strong>{{ statistics.countriesCount }}</strong> countries we show all
        matching events to you. Enable the "Show trip duration" switch to let
        the app calculate the time to get there by car.
      </p>
      <p>
        Each
        <img
          class="inline"
          :src="require('@/assets/marker.svg')"
          style="width: 20px"
        />
        represents an event location.

        <img
          class="inline"
          :src="require('@/assets/clustercircle.svg')"
          style="width: 20px"
        />
        are a cluster of events. Click on it to expand them. Click on the
        <font-awesome-icon icon="search" />
        icon to zoom to the event. Many of the races will have their race
        courses displayed.
      </p>

      <p>
        Additions or corrections can be reported to
        <a href="https://muehlemann.com" target="_blank">me</a> at
        <a href="mailto:silvan@open-water-swims.com"
          >silvan@open-water-swims.com</a
        >.
      </p>
      <p v-if="extended">
        <a href="https://muehlemann.com" target="_blank">Silvan Mühlemann</a>
      </p>

      <p>Thanks to Andrey Sheyko for his collaboration.</p>
    </div>
  </div>
</template>
<script>
import gql from 'graphql-tag'

export default {
  props: {
    extended: {
      type: Boolean,
      default: false,
    },
  },
  apollo: {
    statistics: {
      query: gql`
        query {
          statistics {
            eventCount
            raceCount
            countriesCount
          }
        }
      `,
    },
  },
}
</script>
<style lang="scss">
p {
  @apply my-2;
}
</style>
