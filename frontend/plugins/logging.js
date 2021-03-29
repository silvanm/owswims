import Vue from 'vue'
import LogRocket from 'logrocket'
import * as Sentry from '@sentry/vue'
import { Integrations } from '@sentry/tracing'

Sentry.init({
  Vue,
  dsn: process.env.sentryDSN,
  integrations: [new Integrations.BrowserTracing()],
  tracesSampleRate: 1.0,
})

LogRocket.init('lye1ra/open-water-swimscom')

LogRocket.getSessionURL((sessionURL) => {
  Sentry.configureScope((scope) => {
    scope.setExtra('sessionURL', sessionURL)
  })
})
