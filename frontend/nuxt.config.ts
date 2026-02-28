export default defineNuxtConfig({
  ssr: false,

  app: {
    head: {
      title:
        'open-water-swims.com - Map of Open-Water swim events for Europe, USA and Japan',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'robots', content: 'index' },
        {
          hid: 'description',
          name: 'description',
          content: 'Map of open-water swim events',
        },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'theme-color', content: '#36abff' },
        { property: 'og:url', content: 'https://open-water-swims.com/' },
        { property: 'og:title', content: 'open-water-swims.com' },
        {
          property: 'og:description',
          content: 'Map of open-water swim events for Europe, USA and Japan.',
        },
        {
          property: 'og:image',
          content: 'https://open-water-swims.com/og-image.jpg',
        },
        { property: 'fb:app_id', content: '434576227989037' },
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'manifest', href: '/site.webmanifest' },
        {
          rel: 'shortcut icon',
          sizes: '192x192',
          href: '/android-chrome-192x192.png',
        },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' },
      ],
      script: [{ src: '/fb-sdk.js' }],
    },
    baseURL: '/',
  },

  runtimeConfig: {
    public: {
      googleMapsKey: process.env.GOOGLE_MAPS_API_KEY || '',
      defaultHeaderPhotoUrl:
        process.env.DEFAULT_HEADER_PHOTO_URL ||
        'https://storage.googleapis.com/owswims-prod/photos/default-image.jpg',
      sentryDSN: process.env.SENTRY_DSN || '',
      rapidapiKey: process.env.RAPIDAPI_KEY || '',
      graphqlEndpoint:
        process.env.GRAPHQL_ENDPOINT || 'http://localhost:8000/graphql',
      ciCommitSHA: process.env.CI_COMMIT_SHA || 'local',
    },
  },

  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@nuxtjs/i18n',
    '@nuxtjs/google-fonts',
    'nuxt-gtag',
  ],

  css: ['@fortawesome/fontawesome-svg-core/styles.css'],

  i18n: {
    locales: [
      { code: 'en', iso: 'en-US', file: 'en.json' },
      { code: 'de', iso: 'de-DE', file: 'de.json' },
      { code: 'fr', iso: 'fr-FR', file: 'fr.json' },
      { code: 'it', iso: 'it-IT', file: 'it.json' },
      { code: 'ru', iso: 'ru-RU', file: 'ru.json' },
      { code: 'es', iso: 'es-ES', file: 'es.json' },
      { code: 'ja', iso: 'ja-JP', file: 'ja.json' },
    ],
    defaultLocale: 'en',
    lazy: true,
    langDir: '../app/locales',
    strategy: 'prefix',
    detectBrowserLanguage: {
      useCookie: false,
      cookieKey: 'i18n_redirected',
      onlyOnRoot: true,
    },
  },

  gtag: {
    id: 'UA-10357230-11',
  },

  googleFonts: {
    families: {
      'Source Sans Pro': [400, 600],
    },
  },

  tailwindcss: {},

  nitro: {
    prerender: {
      routes: ['/', '/en', '/de', '/fr', '/it', '/es', '/ru', '/ja'],
    },
  },

  compatibilityDate: '2025-01-01',
})
