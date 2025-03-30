// https://nuxt.com/docs/api/configuration/nuxt-config
// This is a Nuxt 3 configuration file that will be used once the project is migrated to Nuxt 3.
// The TypeScript and ESLint errors are expected at this stage since the project is still using Nuxt 2.

// @ts-ignore - defineNuxtConfig will be available once Nuxt 3 is installed
export default defineNuxtConfig({
  // Disable server-side rendering (same as Nuxt 2 config)
  ssr: false,

  // Compatibility date for Nuxt 3 features
  compatibilityDate: '2024-11-01',

  // Enable devtools for development
  devtools: { enabled: true },

  // Global page headers
  app: {
    head: {
      title: 'open-water-swims.com - Map of European Open-Water swim events',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'robots', content: 'index' },
        {
          name: 'description',
          content: 'Map of open-water swim events in Europe',
        },
        {
          name: 'apple-mobile-web-app-capable',
          content: 'yes',
        },
        {
          name: 'mobile-web-app-capable',
          content: 'yes',
        },
        {
          name: 'theme-color',
          content: '#36abff',
        },
        {
          property: 'og:url',
          content: 'https://open-water-swims.com/',
        },
        {
          property: 'og:title',
          content: 'open-water-swims.com',
        },
        {
          property: 'og:description',
          content: 'Map of open-water swim events in Europe.',
        },
        {
          property: 'og:image',
          content: 'https://open-water-swims.com/static/og-image.jpg',
        },
        {
          property: 'fb:app_id',
          content: '434576227989037',
        },
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/static/favicon.ico' },
        { rel: 'manifest', href: '/static/site.webmanifest' },
        {
          rel: 'shortcut icon',
          sizes: '192x192',
          href: '/static/android-chrome-192x192.png',
        },
        {
          rel: 'apple-touch-icon',
          href: '/static/apple-touch-icon.png',
        },
      ],
      script: [
        {
          src: '/static/fb-sdk.js',
        },
      ],
    },
  },

  // CSS
  css: [
    // Add CSS for Vue 3 compatible components
    '@vueform/slider/themes/default.css',
    '@vuepic/vue-datepicker/dist/main.css',
    'floating-vue/dist/style.css',
  ],

  // Runtime config (replaces env in Nuxt 2)
  runtimeConfig: {
    public: {
      googleMapsKey: process.env.GOOGLE_MAPS_API_KEY,
      defaultHeaderPhotoUrl: 
        process.env.DEFAULT_HEADER_PHOTO_URL || 
        'https://storage.googleapis.com/owswims-prod/photos/default-image.jpg',
      sentryDSN: process.env.SENTRY_DSN,
      rapidapiKey: process.env.RAPIDAPI_KEY,
      ciCommitSHA: process.env.CI_COMMIT_SHA,
      // Apollo configuration
      apollo: {
        clients: {
          default: {
            httpEndpoint: process.env.GRAPHQL_ENDPOINT,
            tokenName: 'apollo-token',
          },
        },
      },
    }
  },

  // Modules
  modules: [
    // Core modules
    '@pinia/nuxt',
    'nuxt-apollo',
    '@nuxtjs/i18n',
    '@nuxtjs/tailwindcss',
    '@nuxtjs/google-fonts',
    '@nuxtjs/fontawesome',
    '@nuxtjs/google-gtag',
  ],

  // Apollo module configuration
  apollo: {
    clients: {
      default: {
        // Use the environment variable from runtimeConfig
        httpEndpoint: process.env.GRAPHQL_ENDPOINT,
        // You can add more configuration options here as needed
        inMemoryCacheOptions: {
          // Configure the InMemoryCache options
        },
        defaultOptions: {
          // Configure default options for queries and mutations
          watchQuery: {
            fetchPolicy: 'cache-and-network',
          },
          query: {
            fetchPolicy: 'network-only',
          },
        },
      },
    },
  },

  // Build configuration
  build: {
    transpile: [
      'floating-vue', 
      '@vuepic/vue-datepicker', 
      '@vueform/slider',
      '@apollo/client',
      'ts-invariant',
      'graphql',
    ],
  },

  // Auto import components (same as Nuxt 2)
  components: true,

  // Google Fonts configuration
  googleFonts: {
    families: {
      'Source Sans Pro': [400, 600],
    },
  },

  // Font Awesome configuration
  fontawesome: {
    icons: {
      solid: [
        'faQuestionCircle',
        'faGripLines',
        'faTimes',
        'faPlus',
        'faSearch',
        'faLocationArrow',
        'faInfoCircle',
        'faImage',
        'faEdit',
        'faExternalLinkSquareAlt',
        'faExpandArrowsAlt',
        'faEnvelope',
        'faArrowLeft',
      ],
      regular: ['faCalendar'],
      brands: ['faFacebook'],
    },
  },

  // Google Analytics configuration
  googleGtag: {
    id: 'UA-10357230-11',
    debug: false,
  },

  // Toast configuration (will need to be updated with a Vue 3 compatible toast library)
  toast: {
    position: 'bottom-center',
    duration: 2000,
  },

  // Router configuration
  router: {
    // Catch-all route will need to be updated for Nuxt 3
    // This will be handled in the pages directory structure
    middleware: ['querystringHandler'],
  },

  // i18n configuration
  i18n: {
    locales: [
      { code: 'en', iso: 'en-US', file: 'en.json' },
      { code: 'de', iso: 'de-DE', file: 'de.json' },
      { code: 'fr', iso: 'fr-FR', file: 'fr.json' },
      { code: 'it', iso: 'it-IT', file: 'it.json' },
      { code: 'ru', iso: 'ru-RU', file: 'ru.json' },
      { code: 'es', iso: 'es-ES', file: 'es.json' },
    ],
    defaultLocale: 'en',
    lazy: true,
    langDir: 'locales/',
    strategy: 'prefix',
    detectBrowserLanguage: {
      useCookie: false,
      cookieKey: 'i18n_redirected',
      onlyOnRoot: true,
    },
  },

  // Vite configuration (new in Nuxt 3)
  vite: {
    // Add any Vite-specific configuration here
  },

  // Plugins configuration
  // Note: Plugins in Nuxt 3 are auto-imported from the plugins directory
  // We'll need to create these plugins in the plugins directory
})
