<template>
  <div v-if="event" class="inline-block">
    <div v-if="flavor === 'summary'" @click="clickOnStars">
      <StarRating
        :rating="average"
        :read-only="true"
        :fixed-points="1"
        :round-start-rating="false"
        :show-rating="false"
        :star-size="15"
        :inline="true"
      ></StarRating>
      <div
        class="inline-block text-normal text-gray mx-1 hover:underline text-blue-600"
        style="position: relative; top: 3px"
      >
        <a v-if="event.reviews.edges.length > 0">
          {{ event.reviews.edges.length }}
          {{ $tc('reviewsCount', event.reviews.edges.length) }}
        </a>
        <a v-else>{{ $t('reviewsRequest') }}</a>
      </div>
    </div>
    <div v-if="flavor === 'expanded'">
      <div class="font-bold text-left">
        <!-- <font-awesome-icon
          @click="$emit('back')"
          icon="arrow-left"
          class="cursor-pointer float-left vertical-middle text-xl"
        ></font-awesome-icon>-->
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
              <StarRating
                :rating="review.rating"
                :show-rating="false"
                :star-size="15"
                :read-only="true"
              ></StarRating>
            </div>
            <div class="px-1" style="padding-top: 2px">
              <country-flag
                :country="review.country.toLowerCase()"
                size="small"
              />
              {{ review.name }}

              <span v-if="review.name || review.country"> </span>
              <span class="text-gray-600">{{
                formattedCreationDate(review.createdAt)
              }}</span>
            </div>
          </div>
          <translatable>{{ review.comment }}</translatable>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import StarRating from 'vue-star-rating'
import { formatDistance } from 'date-fns'
import { localeMap } from '@/constants'
import CountryFlag from 'vue-country-flag'
import Translatable from '@/components/Translatable'

export default {
  name: 'Reviews',
  components: {
    StarRating,
    CountryFlag,
    Translatable,
  },
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
  data() {
    return {
      showModal: false,
    }
  },
  computed: {
    sortedReviews() {
      const result = []
      // @todo make this more elegant
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
        locale: localeMap[this.$i18n.locale],
        addSuffix: true,
      })
    },
    rateEvent() {
      this.$store.commit('focusedEventId', this.event.id)
      this.$store.commit('reviewBoxShown', true)
    },
    clickOnStars() {
      // if there are no events, open the rating window
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
