<template>
  <span>
    <span class="text-to-translate"><slot></slot></span>
    <a @click="translate" v-if="!translationDone" class="cursor-pointer">{{
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
      this.$store.commit('isLoading', true)
      const options = {
        method: 'POST',
        url: 'https://microsoft-translator-text.p.rapidapi.com/translate',
        params: {
          to: this.$i18n.locale,
          'api-version': '3.0',
          profanityAction: 'NoAction',
          textType: 'plain',
        },
        headers: {
          'content-type': 'application/json',
          'x-rapidapi-key':
            '72fd2955fdmshddd25e1282ee77fp199085jsn9326c1622a38',
          'x-rapidapi-host': 'microsoft-translator-text.p.rapidapi.com',
        },
        data: [
          {
            Text: this.$el.getElementsByClassName('text-to-translate')[0]
              .innerHTML,
          },
        ],
      }
      try {
        const response = await axios.request(options)
        this.$el.getElementsByClassName('text-to-translate')[0].innerHTML =
          response.data[0].translations[0].text
        this.translationDone = true
      } catch (e) {}
      this.$store.commit('isLoading', false)
    },
  },
}
</script>
