<template>
  <div>
    <div style="max-width: 600px" class="relative">
      <h1
        v-if="extended"
        class="text-xl md:text-2xl font-semibold text-primary"
      >
        {{ $t('welcomeBoxTitle') }}
      </h1>
      <div class="absolute right-0 bottom-0">
        <button
          v-if="extended"
          class="bg-blue-600 rounded p-2 text-white font-bold float-right"
          @click="$emit('hide')"
        >
          {{ $t('dismiss') }}
        </button>
      </div>
      <p v-if="extended">
        <img
          class="inline float-right"
          src="~/assets/silvan-muehlemann.jpg"
          style="width: 100px; padding-left: 4px"
        />
        {{ $t('infoboxPara1') }}
      </p>
      <p v-if="statistics">
        {{
          $t('infoboxPara2', {
            raceCount: statistics.eventCount,
            countriesCount: statistics.countriesCount,
          })
        }}
      </p>
      <p>
        {{ $t('infoboxPara3') }}
      </p>
      <p>{{ $t('infoboxPara3a') }}</p>
      <p>
        {{ $t('infoboxPara4') }}
        <NuxtLink to="/submit">{{ $t('submissionForm') }}</NuxtLink>
        <a href="mailto:silvan@open-water-swims.com"
          >silvan@open-water-swims.com</a
        >
      </p>

      <p v-if="extended">
        <a href="https://muehlemann.com" target="_blank">Silvan Mühlemann</a>
      </p>
    </div>
  </div>
</template>

<script>
import gql from 'graphql-tag'

const STATISTICS_QUERY = gql`
  query {
    statistics {
      eventCount
      raceCount
      countriesCount
    }
  }
`

export default {
  props: {
    extended: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['hide'],
  setup() {
    const { $apollo } = useNuxtApp()
    return { $apollo }
  },
  data() {
    return {
      statistics: null,
    }
  },
  async mounted() {
    try {
      const result = await this.$apollo.query({ query: STATISTICS_QUERY })
      this.statistics = result.data.statistics
    } catch (error) {
      console.error('Error fetching statistics:', error)
    }
  },
}
</script>

<style lang="scss">
p {
  @apply my-2;
}
</style>
