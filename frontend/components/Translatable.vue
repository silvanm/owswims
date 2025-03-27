<template>
  <span>
    <span class="text-to-translate"><slot></slot></span>
    <a v-if="!translationDone" class="cursor-pointer" @click="translate">{{
      $t('Translate')
    }}</a>
  </span>
</template>
<script>
import axios from 'axios'

export default {
  data() {
    return {
      translationDone: false,
    }
  },
  methods: {
    async translate() {
      this.$gtag('event', 'translate')
      this.$store.commit('isLoading', true)
      const options = {
        method: 'POST',
        url: 'https://google-api31.p.rapidapi.com/gtranslate',
        headers: {
          'content-type': 'application/json',
          'x-rapidapi-key': process.env.rapidapiKey,
          'x-rapidapi-host': 'google-api31.p.rapidapi.com',
        },
        data: {
          text: this.$el.getElementsByClassName('text-to-translate')[0]
            .innerHTML,
          to: this.$i18n.locale,
          from_lang: '',
        },
      }
      try {
        const response = await axios.request(options)
        console.log('Translation response:', response.data)
        // Handle the response based on the Google Translate API format
        if (response.data && response.data.translated_text) {
          this.$el.getElementsByClassName('text-to-translate')[0].innerHTML =
            response.data.translated_text
          this.translationDone = true
          this.$toast.success('Translation completed')
        } else {
          throw new Error('Unexpected response format')
        }
      } catch (e) {
        console.error('Translation error:', e)
        if (e.response) {
          console.error('Response status:', e.response.status)
          console.error('Response data:', e.response.data)
          if (e.response.status === 401) {
            this.$toast.error('Translation service authentication failed')
          } else {
            this.$toast.error(`Translation failed: ${e.response.status}`)
          }
        } else if (e.message) {
          console.error('Error message:', e.message)
          this.$toast.error(`Translation failed: ${e.message}`)
        } else {
          this.$toast.error('Translation failed. Please try again later.')
        }
      }
      this.$store.commit('isLoading', false)
    },
  },
}
</script>
