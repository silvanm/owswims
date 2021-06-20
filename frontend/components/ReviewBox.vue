<template>
  <div
    class="absolute flex items-center justify-center h-screen w-screen"
    style="z-index: 5"
  >
    <div class="p-4 bg-white shadow-xl">
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
          <label class="block">{{ $t('reviewBoxCommentLabel') }}</label>
          <textarea
            id="comment"
            v-model="comment"
            class="block w-full border focus:outline-none p-2"
            rows="4"
          ></textarea>
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
    }
  },
  methods: {
    async postRating() {
      await this.$apollo.mutate({
        mutation: gql`
          mutation($eventId: ID!, $rating: Int!, $comment: String) {
            rateEvent(eventId: $eventId, rating: $rating, comment: $comment) {
              success
            }
          }
        `,
        variables: {
          eventId: this.$store.getters.focusedEventId,
          rating: this.rating,
          comment: this.comment,
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
    width: 300px;
  }

  button {
    @apply bg-blue-600 rounded p-2 text-white font-bold;
  }
}
</style>
