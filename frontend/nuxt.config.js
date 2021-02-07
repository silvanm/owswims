export default {
  // Disable server-side rendering (https://go.nuxtjs.dev/ssr-mode)
  ssr: false,

  // Global page headers (https://go.nuxtjs.dev/config-head)
  head: {
    title: 'European Open-Water Swims',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { name: 'robots', content: 'index' },
      {
        hid: 'description',
        name: 'description',
        content: 'Map of open-water swim events in Europe.',
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
        content: 'European Open-Water Swims',
      },
      {
        property: 'og:description',
        content: 'Map of open-water swim events in Europe.',
      },
      {
        property: 'og:image',
        content: 'https://open-water-swims.com/static/og-image.jpg',
      },
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/static/favicon.ico' },
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
  },

  // Global CSS (https://go.nuxtjs.dev/config-css)
  css: [],

  env: {
    googleMapsKey: process.env.GOOGLE_MAPS_API_KEY,
    defaultHeaderPhotoUrl: process.env.DEFAULT_HEADER_PHOTO_URL,
  },

  // Plugins to run before rendering page (https://go.nuxtjs.dev/config-plugins)
  plugins: [
    {
      src: '~plugins/vue-slider-component.js',
      ssr: false,
    },
    {
      src: '~plugins/vue2-touch-events.js',
      ssr: false,
    },
    {
      src: '~plugins/vue-tooltip.js',
      ssr: false,
    },
    {
      src: '~plugins/deviceDetect.js',
      ssr: false,
    },
    {
      src: '~plugins/vue-easy-lightbox.js',
      ssr: false,
    },
    {
      src: '~plugins/queries.js',
      ssr: false,
    },
  ],

  // Auto import components (https://go.nuxtjs.dev/config-components)
  components: true,

  // Modules for dev and build (recommended) (https://go.nuxtjs.dev/config-modules)
  buildModules: [
    // https://go.nuxtjs.dev/eslint
    '@nuxtjs/eslint-module',
    '@nuxtjs/google-fonts',
    // https://go.nuxtjs.dev/tailwindcss
    '@nuxtjs/tailwindcss',
    '@nuxtjs/fontawesome',
  ],

  // Modules (https://go.nuxtjs.dev/config-modules)
  modules: ['@nuxtjs/apollo', '@nuxtjs/google-gtag', '@nuxtjs/toast'],

  apollo: {
    clientConfigs: {
      default: {
        httpEndpoint: process.env.GRAPHQL_ENDPOINT,
        tokenName: 'apollo-token',
      },
    },
  },

  googleFonts: {
    families: {
      'Source Sans Pro': [400, 600],
    },
  },

  // Build Configuration (https://go.nuxtjs.dev/config-build)
  build: {
    publicPath: '/static/',
  },

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
      ],
    },
  },

  'google-gtag': {
    id: 'UA-10357230-11',
    debug: false,
  },

  toast: {
    position: 'bottom-center',
    duration: 2000,
  },

  router: {
    extendRoutes(routes, resolve) {
      routes.push({
        name: 'custom',
        path: '*',
        component: resolve(__dirname, 'pages/index.vue'),
      })
    },
    middleware: 'querystringHandler',
  },
}
