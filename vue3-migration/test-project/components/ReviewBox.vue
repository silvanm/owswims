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
      <h1 class="font-bold text-xl">{{ t('reviewBoxTitle') }}</h1>
      <form>
        <div class="my-2">
          <StarRating v-model="rating" :show-rating="false"></StarRating>
        </div>
        <div class="my-2">
          <label for="name" class="block">{{ t('reviewBoxNameLabel') }}</label>
          <input id="name" v-model="name" class="block w-full" />
        </div>
        <div class="my-2">
          <label class="block">{{ t('reviewBoxCommentLabel') }}</label>
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
          {{ t('sendButtonLabel') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import StarRating from '@chahindb7/vue-star-rating'
import { useMainStore } from '../stores/main'
import { useToast } from '../composables/useToast'
import { useI18n } from '../composables/useI18n'
import { useQueries } from '../composables/useQueries'
import CloseButton from './CloseButton.vue'

// Define emits
defineEmits(['hide'])

// Setup composables
const store = useMainStore()
const toast = useToast()
const { t } = useI18n()
// We'll use this for mock implementation
const _queries = useQueries()

// Reactive state
const comment = ref('')
const rating = ref(0)
const name = ref('')

// Computed properties
const charactersLeft = computed(() => {
  const char = comment.value.length
  const limit = 1000
  return limit - char + ' / ' + limit
})

// Methods
const postRating = async () => {
  // Mock GraphQL mutation using the useQueries composable
  // In a real implementation, this would use Apollo Client
  try {
    // Log the mutation parameters
    console.log('Submitting review:', {
      eventId: store.focusedEventId,
      rating: rating.value,
      comment: comment.value,
      name: name.value,
      country: store.countryCode,
    })

    // Simulate successful mutation
    await new Promise(resolve => setTimeout(resolve, 500))

    // Show success toast
    toast.success(t('reviewToastThanks'))
    
    // Update store
    store.setReviewBoxShown(false)
    
    // In the original component, this would refresh location data
    // For now, we'll just log it
    console.log('Refreshing location data')
    
    // Analytics tracking (mock)
    console.log('Analytics event: reviewSubmit')
  } catch (error) {
    console.error('Error submitting review:', error)
    toast.error(t('errorSubmittingReview'))
  }
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
