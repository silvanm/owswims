<template>
  <span>
    <span ref="textToTranslate" class="text-to-translate"><slot></slot></span>
    <a v-if="!translationDone" class="cursor-pointer" @click="translate">{{
      $t('Translate')
    }}</a>
  </span>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMainStore } from '~/stores/main'
import { useGtag } from '#imports'
import { useRuntimeConfig } from '#app'
import axios from 'axios'

const { locale } = useI18n()
const store = useMainStore()
const { gtag } = useGtag()
const runtimeConfig = useRuntimeConfig()

const translationDone = ref(false)
const textToTranslate = ref(null)

async function translate() {
  gtag('event', 'translate')
  store.isLoading = true

  const options = {
    method: 'POST',
    url: 'https://google-api31.p.rapidapi.com/gtranslate',
    headers: {
      'content-type': 'application/json',
      'x-rapidapi-key': runtimeConfig.public.rapidapiKey,
      'x-rapidapi-host': 'google-api31.p.rapidapi.com',
    },
    data: {
      text: textToTranslate.value.innerHTML,
      to: locale.value,
      from_lang: '',
    },
  }

  try {
    const response = await axios.request(options)
    console.log('Translation response:', response.data)
    if (response.data && response.data.translated_text) {
      textToTranslate.value.innerHTML = response.data.translated_text
      translationDone.value = true
      console.log('Translation completed')
    } else {
      throw new Error('Unexpected response format')
    }
  } catch (e) {
    console.error('Translation error:', e)
    if (e.response) {
      console.error('Response status:', e.response.status)
      console.error('Response data:', e.response.data)
      if (e.response.status === 401) {
        console.log('Translation service authentication failed')
      } else {
        console.log(`Translation failed: ${e.response.status}`)
      }
    } else if (e.message) {
      console.error('Error message:', e.message)
      console.log(`Translation failed: ${e.message}`)
    } else {
      console.log('Translation failed. Please try again later.')
    }
  }

  store.isLoading = false
}
</script>
