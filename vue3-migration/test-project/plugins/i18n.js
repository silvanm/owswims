// Simple i18n plugin without using vue-i18n
export default defineNuxtPlugin(({ vueApp }) => {
  // Define translations
  const messages = {
    en: {
      poweredBy: 'Powered by',
      tooltipCenterButton: 'Center map on your location',
      tooltipSeeAll: 'See all locations',
      travelTime: 'Travel time',
      noRacesFound: 'No races found. Deactivate some of the filters.',
    },
    de: {
      poweredBy: 'Unterstützt von',
      tooltipCenterButton: 'Karte auf Ihren Standort zentrieren',
      tooltipSeeAll: 'Alle Standorte anzeigen',
      travelTime: 'Reisezeit',
      noRacesFound:
        'Keine Rennen gefunden. Deaktivieren Sie einige der Filter.',
    },
  }

  // Create a simple i18n object
  const i18n = {
    locale: 'en',
    messages,
    t(key) {
      return this.messages[this.locale][key] || key
    },
    setLocale(locale) {
      this.locale = locale
    },
  }

  // Add to global properties
  vueApp.config.globalProperties.$i18n = i18n
  vueApp.provide('i18n', i18n)
})
