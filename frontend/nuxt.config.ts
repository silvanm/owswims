export default defineNuxtConfig({
  ssr: false,

  app: {
    head: {
      title: 'open-water-swims.com - Map of Open-Water swim events',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          hid: 'description',
          name: 'description',
          content: 'Find open-water swimming events near you on an interactive map.',
        },
      ],
    },
    baseURL: '/',
  },

  runtimeConfig: {
    public: {
      googleMapsKey: process.env.GOOGLE_MAPS_API_KEY || '',
      defaultHeaderPhotoUrl:
        process.env.DEFAULT_HEADER_PHOTO_URL ||
        'https://storage.googleapis.com/owswims/media/default_photo.jpg',
      sentryDSN: process.env.SENTRY_DSN || '',
      rapidapiKey: process.env.RAPIDAPI_KEY || '',
      graphqlEndpoint: process.env.GRAPHQL_ENDPOINT || 'http://localhost:8000/graphql',
      ciCommitSHA: process.env.CI_COMMIT_SHA || 'local',
    },
  },

  compatibilityDate: '2025-01-01',
})
