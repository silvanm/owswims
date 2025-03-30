// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // Disable server-side rendering to avoid SSR-related bugs during migration
  ssr: false,
  
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  modules: [
    '@nuxt/content',
    '@nuxt/eslint',
    '@nuxt/fonts',
    '@nuxt/scripts',
    '@nuxt/test-utils',
    '@pinia/nuxt',
    'nuxt-apollo',
    '@nuxtjs/tailwindcss'
  ],

  // CSS
  css: [
    '@vueform/slider/themes/default.css',
    '@vuepic/vue-datepicker/dist/main.css',
    'floating-vue/dist/style.css',
    '~/assets/slider.css',
    '~/assets/v-tooltip.css',
  ],

  // Build configuration
  build: {
    transpile: [
      'floating-vue',
      '@vuepic/vue-datepicker',
      '@vueform/slider',
    ],
  },

  // Module configurations
  runtimeConfig: {
    public: {
      apollo: {
        clients: {
          default: {
            httpEndpoint: 'https://api.example.com/graphql',
          },
        },
      },
    }
  }
})
