<template>
  <div
    class="absolute flex items-center justify-center h-screen w-screen"
    style="z-index: 5"
  >
    <div class="p-4 bg-white shadow-xl w-4/5" style="max-width: 600px">
      <div class="float-right">
        <CloseButton
          ref="closebutton"
          :is-static="true"
          @collapse="$emit('hide')"
        ></CloseButton>
      </div>
      <h1 class="font-bold text-xl">{{ $t('reviewBoxTitle') }}</h1>
      <form>
        <div class="my-2">
          <StarRating v-model="rating" :show-rating="false"></StarRating>
        </div>
        <div class="my-2">
          <label for="name" class="block">{{ $t('reviewBoxNameLabel') }}</label>
          <input id="name" v-model="name" class="block w-full" />
        </div>
        <div class="my-2">
          <label class="block">{{ $t('reviewBoxCommentLabel') }}</label>
          <textarea
            id="comment"
            v-model="comment"
            class="block w-full border p-2"
            rows="4"
            maxlength="1000"
          ></textarea>
          <div class="text-gray-600">{{ charactersLeft }}</div>
        </div>
        <button type="button" @click="postRating">
          {{ $t('sendButtonLabel') }}
        </button>
      </form>
    </div>
  </div>
</template>
<script>
import StarRating from 'vue-star-rating'
import gql from 'graphql-tag'

export default {
  components: {
    StarRating,
  },
  data() {
    return {
      comment: '',
      rating: 0,
      name: '',
    }
  },
  computed: {
    charactersLeft() {
      const char = this.comment.length
      const limit = 1000
      return limit - char + ' / ' + limit
    },
  },
  methods: {
    async postRating() {
      await this.$apollo.mutate({
        mutation: gql`
          mutation(
            $eventId: ID!
            $rating: Int!
            $comment: String
            $name: String
            $country: String
          ) {
            rateEvent(
              eventId: $eventId
              rating: $rating
              comment: $comment
              name: $name
              country: $country
            ) {
              success
            }
          }
        `,
        variables: {
          eventId: this.$store.getters.focusedEventId,
          rating: this.rating,
          comment: this.comment,
          name: this.name,
          country: this.$store.getters.countryCode,
        },
      })

      this.$toast.success(this.$t('reviewToastThanks'))
      this.$store.commit('reviewBoxShown', false)
      this.$store.dispatch('refreshLocationData')
    },
  },
}
</script>
<style lang="scss" scoped>
div {
  input {
    @apply border p-2;
  }

  button {
    @apply bg-blue-600 rounded p-2 text-white font-bold;
  }
}
</style>
