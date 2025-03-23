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
<script>
import gql from 'graphql-tag'

export default {
  data() {
    return {
      sender: '',
      message: '',
      sendButtonMessage: this.$t('sendButtonLabel'),
      sendButtonDisabled: false,
    }
  },
  methods: {
    send() {
      this.sendButtonDisabled = true
      const client = this.$apollo
      client
        .mutate({
          mutation: gql`
            mutation($sender: String!, $message: String!) {
              sendContactmail(sender: $sender, message: $message) {
                ok
                id
              }
            }
          `,
          // Parameters
          variables: {
            sender: this.sender,
            message: this.message,
          },
        })
        .then((result) => {
          if (result.data.sendContactmail.ok) {
            this.sendButtonMessage = this.$t('sendButtonSuccessful')
            window.setTimeout(() => {
              this.$emit('mailsent')
            }, 2000)
          } else {
            this.sendButtonMessage = this.$t('sendButtonFailed')
          }
        })
    },
  },
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
