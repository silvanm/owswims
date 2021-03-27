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
      <p v-if="extended" class="font-semibold">
        <img
          class="inline float-right"
          :src="require('@/assets/silvan-muehlemann.jpg')"
          style="width: 100px; padding-left: 4px"
        />
        {{ $t('infoboxPara1') }}
      </p>
      <p v-if="statistics">
        {{
          $t('infoboxPara2', {
            raceCount: statistics.raceCount,
            countriesCount: statistics.countriesCount,
          })
        }}
      </p>
      <i18n tag="p" path="infoboxPara3">
        <img
          class="inline"
          :src="require('@/assets/marker.svg')"
          style="width: 20px"
        />
        <img
          class="inline"
          :src="require('@/assets/clustercircle.svg')"
          style="width: 20px"
        />
        <font-awesome-icon icon="search" />
      </i18n>
      <i18n tag="p" path="infoboxPara4">
        <a href="https://muehlemann.com" target="_blank">{{ $t('me') }}</a>
        <a href="mailto:silvan@open-water-swims.com"
          >silvan@open-water-swims.com</a
        >
        <a href="https://www.facebook.com/openwaterswims" target="_blank">
          <font-awesome-icon :icon="['fab', 'facebook']" />
        </a>
      </i18n>

      <p v-if="extended">
        <a href="https://muehlemann.com" target="_blank">Silvan Mühlemann</a>
      </p>
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
