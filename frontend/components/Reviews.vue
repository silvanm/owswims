<template>
  <div v-if="event" class="inline-block">
    <div
      v-if="flavor === 'summary'"
      style="padding-bottom: 7px"
      @click="clickOnStars"
    >
      <StarRating
        :rating="average"
        :read-only="true"
        :fixed-points="1"
        :round-start-rating="false"
        :show-rating="false"
        :star-size="18"
      ></StarRating>
    </div>
    <div v-if="flavor === 'expanded'">
      <div class="font-bold text-left">
        <!-- <font-awesome-icon
          @click="$emit('back')"
          icon="arrow-left"
          class="cursor-pointer float-left vertical-middle text-xl"
        ></font-awesome-icon>-->
        <button
          class="cursor-pointer bg-blue-600 rounded p-1 text-white font-bold"
          @click="rateEvent"
        >
          {{ $t('reviewBoxTitle') }}
        </button>
        <button
          class="cursor-pointer rounded p-1 font-bold"
          @click="$emit('back')"
        >
          {{ $t('back') }}
        </button>
      </div>

      <ul>
        <li v-for="review in sortedReviews" :key="review.id">
          <div>
            <div class="inline-block" style="vertical-align: middle">
              <StarRating
                :rating="review.rating"
                :show-rating="false"
                :star-size="15"
                :read-only="true"
              ></StarRating>
            </div>
            <div
              class="inline-block text-gray-600"
              style="vertical-align: middle"
            >
              {{ formattedCreationDate(review.createdAt) }}
            </div>
          </div>
          {{ review.comment }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import StarRating from 'vue-star-rating'
import { formatDistance } from 'date-fns'
import { localeMap } from '@/constants'

export default {
  name: 'Reviews',
  components: {
    StarRating,
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
      console.log(new Date(dt))
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
