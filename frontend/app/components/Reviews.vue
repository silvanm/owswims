<template>
  <div v-if="event" class="inline-block">
    <div v-if="flavor === 'summary'" @click="clickOnStars">
      <!-- Simple star display (replacing vue-star-rating) -->
      <span class="inline-flex items-center">
        <span v-for="i in 5" :key="'avg-' + i" class="text-sm">
          <span v-if="i <= Math.round(average)" class="text-yellow-400">&#9733;</span>
          <span v-else class="text-gray-300">&#9733;</span>
        </span>
      </span>
      <div
        class="inline-block text-normal text-gray mx-1 hover:underline text-blue-600"
        style="position: relative; top: 3px"
      >
        <a v-if="event.reviews.edges.length > 0">
          {{ event.reviews.edges.length }}
          {{ $t('reviewsCount', event.reviews.edges.length) }}
        </a>
        <a v-else>{{ $t('reviewsRequest') }}</a>
      </div>
    </div>
    <div v-if="flavor === 'expanded'">
      <div class="font-bold text-left">
        <button
          class="cursor-pointer bg-blue-600 rounded p-1 px-2 text-white font-bold"
          @click="rateEvent"
        >
          {{ $t('reviewBoxTitle') }}
        </button>
        <button
          class="cursor-pointer rounded p-1 text-blue-600 hover:underline"
          @click="$emit('back')"
        >
          {{ $t('back') }}
        </button>
      </div>

      <ul>
        <li v-for="review in sortedReviews" :key="review.id">
          <div class="mt-2 flex">
            <div>
              <!-- Simple star display for individual review -->
              <span class="inline-flex items-center">
                <span v-for="i in 5" :key="'rev-' + review.id + '-' + i" class="text-sm">
                  <span v-if="i <= review.rating" class="text-yellow-400">&#9733;</span>
                  <span v-else class="text-gray-300">&#9733;</span>
                </span>
              </span>
            </div>
            <div class="px-1" style="padding-top: 2px">
              {{ review.name }}

              <span v-if="review.name || review.country"> </span>
              <span class="text-gray-600">{{
                formattedCreationDate(review.createdAt)
              }}</span>
            </div>
          </div>
          <Translatable>{{ review.comment }}</Translatable>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { formatDistance } from 'date-fns'
import { de, enUS, fr, it, ru, es, ja } from 'date-fns/locale'
import { useMainStore } from '~/stores/main'

const localeMap = { en: enUS, de, fr, it, ru, es, ja }

export default {
  name: 'Reviews',
  props: {
    event: {
      type: Object,
      default: null,
    },
    flavor: {
      type: String,
      default: 'summary',
    },
  },
  emits: ['back'],
  setup() {
    const store = useMainStore()
    const { locale } = useI18n()
    return { store, locale }
  },
  data() {
    return {
      showModal: false,
    }
  },
  computed: {
    sortedReviews() {
      const result = []
      for (let i = this.event.reviews.edges.length; i--; i >= 0) {
        const n = this.event.reviews.edges[i].node
        result.push({
          id: n.id,
          rating: n.rating,
          comment: n.comment,
          createdAt: n.createdAt,
          country: n.country,
          name: n.name,
        })
      }
      return result
    },
    average() {
      if (!this.event) return 0
      return (
        this.event.reviews.edges.reduce(
          (accumulator, currentValue) => accumulator + currentValue.node.rating,
          0.0
        ) / this.event.reviews.edges.length
      )
    },
  },
  methods: {
    formattedCreationDate(dt) {
      return formatDistance(new Date(dt), new Date(), {
        locale: localeMap[this.locale],
        addSuffix: true,
      })
    },
    rateEvent() {
      this.store.focusedEventId = this.event.id
      this.store.reviewBoxShown = true
    },
    clickOnStars() {
      if (this.event.reviews.edges.length === 0) {
        this.rateEvent()
      }
    },
  },
}
</script>

<style scoped>
.scrollable {
  overflow: scroll;
}
</style>
