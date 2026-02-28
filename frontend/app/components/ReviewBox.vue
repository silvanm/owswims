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

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMainStore } from '~/stores/main'
import { useGtag } from '#imports'
import StarRating from 'vue-star-rating'
import gql from 'graphql-tag'

const emit = defineEmits(['hide'])

const { t } = useI18n()
const store = useMainStore()
const { $apollo } = useNuxtApp()
const { gtag } = useGtag()

const comment = ref('')
const rating = ref(0)
const name = ref('')

const charactersLeft = computed(() => {
  const char = comment.value.length
  const limit = 1000
  return limit - char + ' / ' + limit
})

async function postRating() {
  await $apollo.mutate({
    mutation: gql`
      mutation (
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
      eventId: store.focusedEventId,
      rating: rating.value,
      comment: comment.value,
      name: name.value,
      country: store.countryCode,
    },
  })

  gtag('event', 'reviewSubmit')
  console.log(t('reviewToastThanks'))
  store.reviewBoxShown = false
  // TODO: implement refreshLocationData action in main store
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
