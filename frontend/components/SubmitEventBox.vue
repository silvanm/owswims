<template>
  <div
    class="absolute flex items-center justify-center h-screen w-screen"
    style="z-index: 100"
  >
    <div class="p-4 bg-white shadow-xl w-4/5" style="max-width: 500px">
      <div class="float-right">
        <CloseButton
          ref="closebutton"
          :is-static="true"
          @collapse="$emit('hide')"
        ></CloseButton>
      </div>

      <!-- Success state -->
      <div v-if="submitted" class="text-center py-8">
        <div class="text-green-600 text-5xl mb-4">&#10003;</div>
        <p class="text-lg">{{ $t('thankYouSubmission') }}</p>
        <button type="button" class="mt-6" @click="$emit('hide')">
          {{ $t('dismiss') }}
        </button>
      </div>

      <!-- Form state -->
      <div v-else>
        <h1 class="font-bold text-xl mb-2">{{ $t('submitEventTitle') }}</h1>
        <p class="text-gray-600 mb-4">{{ $t('submitEventIntro') }}</p>

        <div class="bg-blue-50 border border-blue-200 rounded p-3 mb-4 text-sm">
          <p class="text-gray-700">
            {{ $t('organizerPortalNote') }}
            <a
              href="/organizer-admin/"
              target="_blank"
              class="text-blue-600 underline"
            >
              {{ $t('organizerPortalLink') }}
            </a>
          </p>
        </div>

        <form @submit.prevent="submitEvent">
          <!-- URL field (required) -->
          <div class="my-3">
            <label for="url" class="block font-medium"
              >{{ $t('eventUrl') }} *</label
            >
            <input
              id="url"
              v-model="url"
              type="url"
              class="block w-full"
              :placeholder="$t('eventUrlPlaceholder')"
              required
            />
            <div v-if="urlError" class="text-red-600 text-sm mt-1">
              {{ urlError }}
            </div>
          </div>

          <!-- Email field (optional) -->
          <div class="my-3">
            <label for="email" class="block font-medium">{{
              $t('yourEmail')
            }}</label>
            <input
              id="email"
              v-model="email"
              type="email"
              class="block w-full"
              :placeholder="$t('yourEmailPlaceholder')"
            />
          </div>

          <!-- Comment field (optional) -->
          <div class="my-3">
            <label for="comment" class="block font-medium">{{
              $t('commentLabel')
            }}</label>
            <textarea
              id="comment"
              v-model="comment"
              class="block w-full border p-2"
              rows="3"
              maxlength="1000"
              :placeholder="$t('commentPlaceholder')"
            ></textarea>
          </div>

          <button type="submit" :disabled="isSubmitting">
            <span v-if="isSubmitting">...</span>
            <span v-else>{{ $t('submit') }}</span>
          </button>
        </form>
      </div>
    </div>
    <div
      class="absolute h-screen w-screen bg-black opacity-25"
      style="z-index: -1; top: 0"
      @click="$emit('hide')"
    ></div>
  </div>
</template>

<script>
import gql from 'graphql-tag'

export default {
  data() {
    return {
      url: '',
      email: '',
      comment: '',
      urlError: '',
      isSubmitting: false,
      submitted: false,
    }
  },
  methods: {
    validateUrl() {
      this.urlError = ''

      if (!this.url.trim()) {
        this.urlError = this.$t('urlRequired')
        return false
      }

      // Basic URL validation
      try {
        const urlObj = new URL(this.url)
        if (!['http:', 'https:'].includes(urlObj.protocol)) {
          this.urlError = this.$t('invalidUrl')
          return false
        }
      } catch (e) {
        this.urlError = this.$t('invalidUrl')
        return false
      }

      return true
    },

    async submitEvent() {
      if (!this.validateUrl()) {
        return
      }

      this.isSubmitting = true

      try {
        await this.$apollo.mutate({
          mutation: gql`
            mutation ($url: String!, $email: String, $comment: String) {
              submitEventUrl(url: $url, email: $email, comment: $comment) {
                success
                message
              }
            }
          `,
          variables: {
            url: this.url,
            email: this.email || null,
            comment: this.comment || null,
          },
        })

        this.$gtag('event', 'eventSubmit')
        this.submitted = true
      } catch (error) {
        console.error('Error submitting event:', error)
        this.$toast.error('An error occurred. Please try again.')
      } finally {
        this.isSubmitting = false
      }
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

    &:disabled {
      @apply opacity-50 cursor-not-allowed;
    }
  }
}
</style>
