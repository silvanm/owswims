<template>
  <div>
    <p>{{ $t('contactIntro') }}</p>
    <label class="block font-semibold pt-4" for="sender">
      <div class="pb-2">{{ $t('contactEmail') }}</div>
      <input id="sender" v-model="sender" type="text" />
    </label>
    <label class="block font-semibold pb-2 pt-4">
      <div class="pb-2">{{ $t('contactMessage') }}</div>
      <textarea id="message" v-model="message" class="h-24"></textarea>
    </label>
    <button
      type="button"
      :class="{ 'mr-2': true, disabled: sendButtonDisabled }"
      :disabled="sendButtonDisabled"
      @click="send"
    >
      {{ sendButtonMessage }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import gql from 'graphql-tag'

const emit = defineEmits(['mailsent'])

const { t } = useI18n()
const { $apollo } = useNuxtApp()

const sender = ref('')
const message = ref('')
const sendButtonMessage = ref(t('sendButtonLabel'))
const sendButtonDisabled = ref(false)

async function send() {
  sendButtonDisabled.value = true
  try {
    const result = await $apollo.mutate({
      mutation: gql`
        mutation ($sender: String!, $message: String!) {
          sendContactmail(sender: $sender, message: $message) {
            ok
            id
          }
        }
      `,
      variables: {
        sender: sender.value,
        message: message.value,
      },
    })

    if (result.data.sendContactmail.ok) {
      sendButtonMessage.value = t('sendButtonSuccessful')
      window.setTimeout(() => {
        emit('mailsent')
      }, 2000)
    } else {
      sendButtonMessage.value = t('sendButtonFailed')
      sendButtonDisabled.value = false
    }
  } catch (e) {
    console.error('Contact form send error:', e)
    sendButtonMessage.value = t('sendButtonFailed')
    sendButtonDisabled.value = false
  }
}
</script>

<style lang="scss" scoped>
div {
  input,
  textarea {
    @apply block inline-flex border p-2 w-full;
  }

  button {
    @apply bg-blue-600 rounded p-2 text-white font-bold;
  }

  .disabled {
    @apply opacity-50 cursor-not-allowed;
  }
}
</style>
