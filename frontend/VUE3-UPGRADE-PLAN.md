# Vue 3 / Nuxt Upgrade Plan

> **Date:** 2026-02-27
> **Current stack:** Nuxt 2.18 / Vue 2 / Vuex 3 / Options API
> **Target stack:** Nuxt 4.x / Vue 3 / Pinia / Composition API

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current Architecture Audit](#2-current-architecture-audit)
3. [Migration Strategy: Nuxt 4 (not Nuxt 3)](#3-migration-strategy-nuxt-4-not-nuxt-3)
4. [Phase 0 — Preparation (before migration)](#4-phase-0--preparation)
5. [Phase 1 — Project Skeleton & Configuration](#5-phase-1--project-skeleton--configuration)
6. [Phase 2 — Core Infrastructure](#6-phase-2--core-infrastructure)
7. [Phase 3 — Component Migration](#7-phase-3--component-migration)
8. [Phase 4 — State Management (Vuex → Pinia)](#8-phase-4--state-management-vuex--pinia)
9. [Phase 5 — Plugin & Middleware Migration](#9-phase-5--plugin--middleware-migration)
10. [Phase 6 — Third-Party Package Replacements](#10-phase-6--third-party-package-replacements)
11. [Phase 7 — Testing, Polish & Deployment](#11-phase-7--testing-polish--deployment)
12. [Dependency Migration Map](#12-dependency-migration-map)
13. [Component-by-Component Migration Notes](#13-component-by-component-migration-notes)
14. [Risk Assessment](#14-risk-assessment)
15. [Decisions to Make](#15-decisions-to-make)

---

## 1. Executive Summary

The frontend runs on **Nuxt 2.18** (Vue 2, Webpack, Vuex). Nuxt 3 reached EOL on July 31, 2026, and **Nuxt 4 is the current active major version**. This plan targets a **direct migration to Nuxt 4** (Vue 3), skipping Nuxt 3 / Nuxt Bridge.

**Why skip Nuxt 3 / Nuxt Bridge?**
- Nuxt 3 is already in maintenance mode and approaching EOL.
- Nuxt Bridge was intended as a stepping stone but adds complexity without long-term benefit.
- Nuxt 4 is stable (v4.3) and the recommended target for new migrations.
- The codebase is small enough (~3,500 lines of Vue code, 22 components) to migrate directly.

**Key positive findings from the audit:**
- No `Vue.set()` / `Vue.delete()` usage
- No `.sync` modifier, `.native` modifier, or `v-on="$listeners"` patterns
- No render functions or JSX
- No global filters
- No event bus patterns
- Tailwind CSS (fully compatible — no CSS framework migration needed)
- SPA mode (`ssr: false`) simplifies the migration (no SSR hydration concerns)
- Small Vuex store (2 modules, ~185 lines total)

---

## 2. Current Architecture Audit

### 2.1 Dependencies Requiring Migration

| Package | Current Version | Status | Replacement |
|---------|----------------|--------|-------------|
| `nuxt` | ^2.18.1 | Vue 2 only | `nuxt` ^4.x |
| `@nuxtjs/apollo` | ^4.0.1-rc.5 | Inactive/abandoned | Manual `@apollo/client` + `@vue/apollo-composable` |
| `nuxt-i18n` | ^6.20.1 | Vue 2 only | `@nuxtjs/i18n` ^9.x |
| `vue2-datepicker` | ^3.9.0 | Vue 2 only | `vue-datepicker-next` or `@vuepic/vue-datepicker` |
| `vue2-touch-events` | ^3.1.0 | Vue 2 only | Custom composable or `@vueuse/gesture` |
| `vue-easy-lightbox` | 0.x | Vue 2 only | `vue-easy-lightbox` ^1.x (has Vue 3 support) |
| `vue-slider-component` | ^3.2.9 | Vue 2 only | `vue-3-slider-component` or `@vueform/slider` |
| `vue-star-rating` | ^1.7.0 | Vue 2 only | `vue-star-rating` ^2.x (Vue 3) |
| `vue-tour` | ^1.5.0 | Vue 2 only | `vue3-tour` or `driver.js` |
| `vue-country-flag` | ^2.1.1 | Vue 2 only | `vue-country-flag-next` ^2.x |
| `v-tooltip` | ^2.0.3 | Vue 2 only | `floating-vue` (same author, Vue 3) |
| `vue-loading-template` | ^1.3.2 | Vue 2 only | CSS spinner or `vue-loading-overlay` v6 |
| `@nuxtjs/toast` | ^3.3.1 | Nuxt 2 only | `vue-toastification` v2 or `nuxt-toast` |
| `@nuxtjs/google-gtag` | ^1.0.4 | Nuxt 2 only | `nuxt-gtag` for Nuxt 3/4 |
| `@sentry/vue` | ^7.0.0 | OK | Upgrade to `@sentry/vue` ^8.x + `@sentry/nuxt` |
| `apollo-cache-inmemory` | ^1.6.6 | Apollo 2 | Included in `@apollo/client` ^3.x |
| `@nuxtjs/tailwindcss` | ^4.2.1 | Nuxt 2 | `@nuxtjs/tailwindcss` ^6.x |
| `@nuxtjs/google-fonts` | ^1.1.3 | Nuxt 2 | `@nuxtjs/google-fonts` ^3.x or `@nuxtjs/fonts` |
| `@nuxtjs/fontawesome` | ^1.1.2 | Nuxt 2 | Manual setup or `@vesp/nuxt-fontawesome` |
| `@googlemaps/markerclustererplus` | ^1.0.3 | OK | `@googlemaps/markerclusterer` (newer) |

### 2.2 Vue 2 Patterns Found in Code

| Pattern | Location | Migration Action |
|---------|----------|-----------------|
| `beforeDestroy()` | `CourseEditor.vue` | Rename to `onBeforeUnmount()` |
| `Vue.component()` global registration | 3 plugins | Use `app.component()` or auto-imports |
| `Vue.use()` global plugin install | 3 plugins | Use `app.use()` in Nuxt plugin |
| Options API (`data`, `computed`, `watch`, `methods`) | All 22 components | Keep (still works) or migrate to Composition API |
| `this.$store` | Throughout | Replace with `useStore()` / Pinia composables |
| `this.$apollo` | ~10 components | Replace with `useQuery()` / `useMutation()` composables |
| `this.$t()` / `this.$i18n` | Throughout | Replace with `useI18n()` composable |
| `this.$router` / `this.$route` | Several components | Replace with `useRouter()` / `useRoute()` |
| `this.$refs` | Several components | Keep (works in Vue 3) or use template refs |
| `this.$el` | `Translatable.vue` | Use template ref instead |
| `this.$toast` | Several components | Replace with new toast library |
| `this.$gtag()` | Several components | Replace with `useGtag()` composable |
| Apollo `apollo:` option | 4 components | Replace with `useQuery()` composable |
| `head()` method | `layouts/default.vue` | Replace with `useHead()` / `useSeoMeta()` |
| Mixin `eventPresentation.js` | 2 components | Convert to composable |

### 2.3 Files by Migration Effort

**Trivial** (< 30 min each):
- `Toggle.vue`, `Spinner.vue`, `CloseButton.vue`, `Ribbon.vue`, `OrganizerLogo.vue`, `WelcomeBox.vue`

**Easy** (30 min – 1 hour each):
- `LoginBox.vue`, `ContactForm.vue`, `ReviewBox.vue`, `Translatable.vue`, `InfoTab.vue`, `Infotext.vue`

**Medium** (1–3 hours each):
- `SubmitEventBox.vue`, `Reviews.vue`, `OrganizerSelector.vue`, `DaterangeSlider.vue`, `FilterBox.vue`, `CourseEditor.vue`

**Complex** (3–8 hours each):
- `EventPane.vue` (581 lines, Apollo, mixins, touch events, complex watchers)
- `Map.vue` (638 lines, Google Maps API, marker clustering, complex state)

---

## 3. Migration Strategy: Nuxt 4 (not Nuxt 3)

### Approach: Fresh Nuxt 4 project, incremental component porting

We will create a **new Nuxt 4 project** alongside the existing Nuxt 2 code, then port components one by one. This is cleaner than an in-place upgrade because:

1. Nuxt 4 has a different directory structure (`app/` directory)
2. Config format is completely different (`nuxt.config.ts` with `defineNuxtConfig`)
3. Module system is different (no `buildModules` vs `modules` distinction)
4. Clean break avoids half-migrated states that are hard to debug

### Options API vs Composition API

Vue 3 / Nuxt 4 **fully supports Options API**. We don't need to rewrite every component to Composition API. The strategy:

- **Simple components**: Keep Options API (it works fine in Vue 3)
- **Complex components** (Map, EventPane): Migrate to Composition API for better maintainability
- **New code**: Write in Composition API with `<script setup>`
- **Mixins**: Convert to composables (required — mixins are discouraged in Vue 3)

---

## 4. Phase 0 — Preparation

> **Goal:** Reduce risk before starting the migration

### 4.1 Lock down the current app
- [ ] Ensure the current Nuxt 2 app builds and deploys cleanly
- [ ] Document all environment variables used by the frontend
- [ ] Take screenshots / recordings of all pages and states for regression testing
- [ ] Ensure Cypress tests pass (or update them to pass)

### 4.2 Pre-migration refactors in Nuxt 2 (optional, reduces migration work)
- [ ] Replace `beforeDestroy` with `beforeUnmount` (works in Vue 2.7+)
- [ ] Extract the `eventPresentation` mixin into standalone utility functions (pure JS, no `this`)
- [ ] Remove any unused components or dead code
- [ ] Audit and remove unused npm dependencies

### 4.3 Create a migration branch
- [ ] Create a long-lived `feat/nuxt4-migration` branch
- [ ] Keep the Nuxt 2 app deployable on `main` throughout migration

---

## 5. Phase 1 — Project Skeleton & Configuration

> **Goal:** Bootable Nuxt 4 project with routing, build, and deploy working

### 5.1 Initialize Nuxt 4 project

```bash
npx nuxi@latest init frontend-v4
```

This creates the Nuxt 4 project structure:

```
frontend-v4/
├── app/
│   ├── pages/
│   ├── components/
│   ├── composables/
│   ├── layouts/
│   ├── middleware/
│   ├── plugins/
│   └── app.vue
├── public/           # replaces static/
├── server/           # not needed for SPA
├── nuxt.config.ts
├── package.json
└── tsconfig.json
```

### 5.2 Configure `nuxt.config.ts`

```typescript
export default defineNuxtConfig({
  ssr: false,  // SPA mode (same as current)

  app: {
    head: {
      // Move current head config here
      title: 'open-water-swims.com - Map of Open-Water swim events',
      meta: [/* ... current meta tags ... */],
      link: [/* ... current link tags ... */],
      script: [/* ... fb-sdk etc ... */],
    },
    baseURL: '/',
  },

  // Runtime config replaces env property
  runtimeConfig: {
    public: {
      googleMapsKey: process.env.GOOGLE_MAPS_API_KEY,
      defaultHeaderPhotoUrl: process.env.DEFAULT_HEADER_PHOTO_URL || '...',
      sentryDSN: process.env.SENTRY_DSN,
      rapidapiKey: process.env.RAPIDAPI_KEY,
      graphqlEndpoint: process.env.GRAPHQL_ENDPOINT,
    },
  },

  modules: [
    '@nuxtjs/i18n',
    '@nuxtjs/tailwindcss',
    '@nuxtjs/google-fonts',
    'nuxt-gtag',
  ],

  i18n: {
    locales: [
      { code: 'en', iso: 'en-US', file: 'en.json' },
      { code: 'de', iso: 'de-DE', file: 'de.json' },
      // ... same locale config
    ],
    defaultLocale: 'en',
    lazy: true,
    langDir: 'locales/',
    strategy: 'prefix',
  },

  gtag: {
    id: 'UA-10357230-11',
  },

  googleFonts: {
    families: {
      'Source Sans Pro': [400, 600],
    },
  },

  tailwindcss: {
    // Tailwind config
  },
})
```

### 5.3 Set up build and deployment

- [ ] Update `Dockerfile` to build from `frontend-v4/` (or rename)
- [ ] Update `deploy.yml` GitHub Actions workflow
- [ ] Verify `npm run build` and `npm run generate` work
- [ ] Verify static file serving (public/ directory)

### 5.4 Milestone: Empty Nuxt 4 app loads in browser

---

## 6. Phase 2 — Core Infrastructure

> **Goal:** Apollo GraphQL, i18n, auth, and routing working

### 6.1 Apollo Client Setup (Manual)

Since `@nuxtjs/apollo` is abandoned, set up Apollo manually:

```bash
npm install @apollo/client @vue/apollo-composable graphql graphql-tag
```

Create `app/plugins/apollo.ts`:

```typescript
import { defineNuxtPlugin, useRuntimeConfig } from '#app'
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client/core'
import { DefaultApolloClient } from '@vue/apollo-composable'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()

  const httpLink = createHttpLink({
    uri: config.public.graphqlEndpoint,
  })

  const cache = new InMemoryCache()

  const apolloClient = new ApolloClient({
    link: httpLink,
    cache,
  })

  // Provide to Vue app
  nuxtApp.vueApp.provide(DefaultApolloClient, apolloClient)

  // Also make available as $apollo for backward compat during migration
  return {
    provide: {
      apollo: apolloClient,
    },
  }
})
```

**Component usage changes:**

```vue
<!-- Before (Nuxt 2 / Options API) -->
<script>
export default {
  apollo: {
    locations: {
      query: LOCATIONS_QUERY,
      variables() { return { ... } },
    },
  },
}
</script>

<!-- After (Nuxt 4 / Composition API) -->
<script setup>
import { useQuery } from '@vue/apollo-composable'
import { LOCATIONS_QUERY } from '~/graphql/queries'

const { result, loading, error } = useQuery(LOCATIONS_QUERY, () => ({ ... }))
const locations = computed(() => result.value?.locationsFiltered ?? [])
</script>
```

### 6.2 Internationalization (@nuxtjs/i18n v9)

```bash
npm install @nuxtjs/i18n
```

- Copy `locales/*.json` files to `app/locales/`
- Configuration goes in `nuxt.config.ts` (see Phase 1)
- Template usage (`{{ $t('key') }}`) remains the same
- Script usage changes in `<script setup>`:

```typescript
const { t, locale } = useI18n()
// instead of this.$t('key')
t('key')
```

### 6.3 Authentication

Convert the Vuex auth module to a composable (`app/composables/useAuth.ts`) or Pinia store:

```typescript
// app/composables/useAuth.ts
export function useAuth() {
  const user = useState<User | null>('auth-user', () => null)
  const loggedIn = computed(() => !!user.value)

  async function login(username: string, password: string) {
    const { $apollo } = useNuxtApp()
    const result = await $apollo.mutate({ mutation: LOGIN_MUTATION, variables: { username, password } })
    // Handle token storage and user state
  }

  async function logout() {
    // Clear token and state
  }

  return { user, loggedIn, login, logout }
}
```

### 6.4 Routing & Middleware

**Middleware migration** (`app/middleware/querystringHandler.ts`):

```typescript
// Nuxt 2: export default function (context) { ... }
// Nuxt 4: export default defineNuxtRouteMiddleware((to, from) => { ... })

export default defineNuxtRouteMiddleware(async (to, from) => {
  // Access store via Pinia
  const store = useMainStore()
  // Parse query params and update store
  // ...
})
```

**Router catch-all** for SPA:
In Nuxt 4, use a catch-all page: `app/pages/[...slug].vue`

### 6.5 Milestone: App loads with i18n, Apollo fetches data, routes work

---

## 7. Phase 3 — Component Migration

> **Goal:** All components ported and rendering correctly

### 7.1 Migration order (dependency-based)

Migrate leaf components first, then work up to page-level components:

**Wave 1 — Leaf components (no store/Apollo dependencies):**
1. `Toggle.vue`
2. `Spinner.vue`
3. `CloseButton.vue`
4. `Ribbon.vue`
5. `OrganizerLogo.vue`

**Wave 2 — Simple components with store/Apollo:**
6. `WelcomeBox.vue`
7. `LoginBox.vue`
8. `ContactForm.vue`
9. `ReviewBox.vue`
10. `Translatable.vue`

**Wave 3 — Medium components:**
11. `InfoTab.vue`
12. `Infotext.vue`
13. `Reviews.vue`
14. `OrganizerSelector.vue`
15. `SubmitEventBox.vue`
16. `DaterangeSlider.vue` (blocked on datepicker replacement)

**Wave 4 — Complex components:**
17. `FilterBox.vue`
18. `CourseEditor.vue`
19. `EventPane.vue` (depends on mixin → composable conversion)
20. `Map.vue` (depends on mixin → composable conversion)

**Wave 5 — Pages & Layout:**
21. `layouts/default.vue`
22. `pages/index.vue`

### 7.2 General component migration steps

For each component:

1. Copy `.vue` file to new location under `app/components/`
2. Replace `beforeDestroy` → `onBeforeUnmount` (if present)
3. Replace `this.$store` → Pinia store composable calls
4. Replace `this.$t()` → `useI18n()` composable (or keep `$t` in template — it still works)
5. Replace `apollo:` option → `useQuery()` / `useMutation()` composables
6. Replace `this.$toast` → new toast API
7. Replace `this.$router` / `this.$route` → `useRouter()` / `useRoute()` (or keep in template)
8. Test rendering and interactions
9. Optionally convert to `<script setup>` for cleaner code

### 7.3 Mixin → Composable conversion

Convert `mixins/eventPresentation.js` to `app/composables/useEventPresentation.ts`:

```typescript
// app/composables/useEventPresentation.ts
import { format } from 'date-fns'

export function useEventPresentation() {
  const { locale } = useI18n()
  const store = useMainStore()

  function formatEventDate(event: any) {
    // ... same logic, but using locale.value instead of this.$i18n.locale
  }

  function calculateDistance(lat: number, lng: number) {
    // ... same logic, but using store.location instead of this.$store.getters.location
  }

  return { formatEventDate, calculateDistance, /* ... other methods */ }
}
```

---

## 8. Phase 4 — State Management (Vuex → Pinia)

> **Goal:** Replace Vuex with Pinia

### 8.1 Install Pinia

Pinia is included with Nuxt 4 by default — no extra installation needed.

### 8.2 Main store migration

```typescript
// app/stores/main.ts
export const useMainStore = defineStore('main', () => {
  // State (replaces data/state)
  const location = ref({ lat: 47.36, lng: 8.53 })
  const selectedEventSlug = ref(null)
  const filterDistance = ref(null)
  const filterDistanceMax = ref(2000)
  // ... other state properties

  // Getters (replaces getters)
  // In Pinia with setup syntax, use computed()

  // Actions (replaces mutations + actions)
  async function locateMe() {
    // ... geolocation logic
  }

  async function refreshLocationData() {
    // ... GraphQL query logic
  }

  return {
    location, selectedEventSlug, filterDistance, filterDistanceMax,
    locateMe, refreshLocationData,
  }
})
```

### 8.3 Auth store migration

```typescript
// app/stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loggedIn = computed(() => !!user.value)

  async function login(username: string, password: string) { /* ... */ }
  function logout() { /* ... */ }

  return { user, loggedIn, login, logout }
})
```

### 8.4 Component updates

```typescript
// Before (Vuex)
this.$store.getters.selectedEventSlug
this.$store.commit('setSelectedEventSlug', slug)
this.$store.dispatch('locateMe')

// After (Pinia)
const store = useMainStore()
store.selectedEventSlug          // direct access
store.selectedEventSlug = slug   // direct mutation (no commit needed!)
store.locateMe()                 // actions are just methods
```

---

## 9. Phase 5 — Plugin & Middleware Migration

### 9.1 Plugin migration table

| Nuxt 2 Plugin | Migration | Nuxt 4 Equivalent |
|---------------|-----------|-------------------|
| `fontawesome.js` | Module-based setup | `app/plugins/fontawesome.ts` with `library.add()` + `app.component()` |
| `logging.js` (Sentry) | Use `@sentry/nuxt` module | `modules: ['@sentry/nuxt/module']` in config |
| `vue-slider-component.js` | Replace package | Auto-import or `app.component()` in plugin |
| `vue2-touch-events.js` | Replace with composable | `app/composables/useTouch.ts` |
| `vue-tooltip.js` | Upgrade to floating-vue | `app/plugins/floating-vue.ts` |
| `deviceDetect.js` | Convert to composable | `app/composables/useDevice.ts` |
| `vue-easy-lightbox.js` | Upgrade to v1.x | Auto-import or plugin registration |
| `queries.js` | Convert to composable | `app/composables/useQueries.ts` |
| `urlHistory.js` | Convert to composable | `app/composables/useUrlHistory.ts` |

### 9.2 Nuxt 4 plugin format

```typescript
// app/plugins/example.ts
export default defineNuxtPlugin((nuxtApp) => {
  // nuxtApp.vueApp is the Vue 3 app instance
  nuxtApp.vueApp.use(SomePlugin)
  nuxtApp.vueApp.component('SomeComponent', SomeComponent)

  // Provide helpers (replaces inject)
  return {
    provide: {
      myHelper: () => { /* ... */ },
    },
  }
})
```

### 9.3 Middleware migration

The `querystringHandler` middleware needs conversion to Nuxt 4 format:

```typescript
// app/middleware/querystringHandler.global.ts
export default defineNuxtRouteMiddleware(async (to, from) => {
  const store = useMainStore()
  const { $apollo } = useNuxtApp()

  // Parse query params
  if (to.query.organizer) {
    // Fetch organizer data via Apollo
  }
  if (to.query.event) {
    // Fetch event data via Apollo
  }
  // ... rest of querystring handling logic
})
```

---

## 10. Phase 6 — Third-Party Package Replacements

### 10.1 Datepicker (`vue2-datepicker` → `@vuepic/vue-datepicker`)

```bash
npm install @vuepic/vue-datepicker
```

`@vuepic/vue-datepicker` is the most popular Vue 3 datepicker. It supports date ranges, i18n, and custom styling. The `DaterangeSlider.vue` component will need its template updated to match the new component's API.

### 10.2 Touch events (`vue2-touch-events` → custom composable)

Create a lightweight touch composable instead of a full library:

```typescript
// app/composables/useSwipe.ts
export function useSwipe(el: Ref<HTMLElement | null>, options?: SwipeOptions) {
  // Implement swipe detection using pointer events
  // Used only in EventPane.vue
}
```

Alternatively, use `@vueuse/gesture` or `@vueuse/core`'s `useSwipe`.

### 10.3 Tooltip (`v-tooltip` → `floating-vue`)

```bash
npm install floating-vue
```

Same author — `floating-vue` is the Vue 3 successor to `v-tooltip`. The `v-tooltip` directive name is preserved, so template changes are minimal.

### 10.4 Lightbox (`vue-easy-lightbox` 0.x → 1.x)

```bash
npm install vue-easy-lightbox@^1
```

`vue-easy-lightbox` v1.x supports Vue 3. API is similar but check for breaking changes in props/events.

### 10.5 Star rating (`vue-star-rating` → v2.x)

```bash
npm install vue-star-rating@^2
```

Vue 3 version with largely the same API.

### 10.6 Slider (`vue-slider-component` → `@vueform/slider`)

```bash
npm install @vueform/slider
```

Modern, well-maintained Vue 3 slider. Alternative: `vue-3-slider-component`.

### 10.7 Country flag (`vue-country-flag` → `vue-country-flag-next`)

```bash
npm install vue-country-flag-next
```

### 10.8 Toast notifications (`@nuxtjs/toast` → `vue-toastification`)

```bash
npm install vue-toastification@^2
```

### 10.9 Tour (`vue-tour` → `driver.js`)

```bash
npm install driver.js
```

`driver.js` is framework-agnostic, well-maintained, and provides a better UX. If Vue-specific integration is preferred, `vue3-tour` is available but less actively maintained.

### 10.10 Google Maps marker clustering

```bash
npm install @googlemaps/markerclusterer
```

The newer `@googlemaps/markerclusterer` replaces `@googlemaps/markerclustererplus`. The API is slightly different (uses `Renderer` interface instead of styles/calculator).

---

## 11. Phase 7 — Testing, Polish & Deployment

### 11.1 Visual regression testing
- [ ] Compare screenshots of every state against the Nuxt 2 app
- [ ] Test all language variants
- [ ] Test mobile and desktop viewports

### 11.2 Functional testing
- [ ] Map loads and displays markers correctly
- [ ] Marker clustering works
- [ ] Event pane opens/closes with swipe and click
- [ ] All filters work (date range, distance, keyword, organizer)
- [ ] Course editor draws tracks on map
- [ ] Reviews display and submission works
- [ ] Login/logout flow works
- [ ] Contact form submits
- [ ] Event submission form works
- [ ] i18n language switching works
- [ ] URL query parameters populate state correctly
- [ ] Deep links (event slug, organizer slug) work
- [ ] Google Analytics events fire

### 11.3 Cypress test updates
- [ ] Update selectors if component structure changed
- [ ] Update any Nuxt-specific test helpers
- [ ] Verify all existing tests pass

### 11.4 Performance checks
- [ ] Bundle size comparison (Nuxt 4 + Vite should be smaller)
- [ ] Lighthouse score comparison
- [ ] Map rendering performance with many markers

### 11.5 Deployment
- [ ] Update Docker build for Nuxt 4 (Vite instead of Webpack)
- [ ] Update Helm chart if static file paths changed
- [ ] Update `public/` path configuration
- [ ] Update GitHub Actions workflow
- [ ] Deploy to staging environment first
- [ ] Smoke test on staging
- [ ] Deploy to production

---

## 12. Dependency Migration Map

### Final `package.json` dependencies (estimated)

```json
{
  "dependencies": {
    "@apollo/client": "^3.x",
    "@vue/apollo-composable": "^4.x",
    "@vuepic/vue-datepicker": "^9.x",
    "@vueform/slider": "^2.x",
    "@googlemaps/markerclusterer": "^2.x",
    "date-fns": "^2.30.0",
    "driver.js": "^1.x",
    "floating-vue": "^5.x",
    "graphql": "^16.x",
    "graphql-tag": "^2.x",
    "lodash-es": "^4.x",
    "vue-country-flag-next": "^2.x",
    "vue-easy-lightbox": "^1.x",
    "vue-star-rating": "^2.x",
    "vue-toastification": "^2.x"
  },
  "devDependencies": {
    "@nuxtjs/i18n": "^9.x",
    "@nuxtjs/tailwindcss": "^6.x",
    "@nuxtjs/google-fonts": "^3.x",
    "@sentry/nuxt": "^8.x",
    "nuxt": "^4.x",
    "nuxt-gtag": "^3.x",
    "cypress": "^13.x",
    "eslint": "^9.x",
    "@nuxt/eslint": "^0.x",
    "prettier": "^3.x",
    "typescript": "^5.x"
  }
}
```

---

## 13. Component-by-Component Migration Notes

### `Map.vue` (638 lines) — HIGH effort

**Current:** Options API, `eventPresentation` mixin, Google Maps API with MarkerClusterer, complex watchers for map state.

**Migration plan:**
- Convert to `<script setup>` with Composition API
- Replace mixin with `useEventPresentation()` composable
- Replace `this.$store` with `useMainStore()` Pinia store
- Replace `@googlemaps/markerclustererplus` with `@googlemaps/markerclusterer`
- Google Maps initialization: use `onMounted()` instead of `mounted()`
- Convert watchers to `watch()` composable function
- Consider extracting map initialization into `useGoogleMaps()` composable

### `EventPane.vue` (581 lines) — HIGH effort

**Current:** Options API, Apollo `apollo:` option, `eventPresentation` mixin, `vue2-touch-events`, complex watchers.

**Migration plan:**
- Convert to `<script setup>` with Composition API
- Replace `apollo:` option with `useQuery()` composable
- Replace mixin with `useEventPresentation()` composable
- Replace `v-touch:swipe` with custom `useSwipe()` composable
- Replace `this.$store` with Pinia
- Convert watchers to `watch()` composable

### `FilterBox.vue` (298 lines) — MEDIUM effort

**Current:** Options API, store-heavy with watchers and computed.

**Migration plan:**
- Migrate to `<script setup>`
- Replace store access with Pinia composable
- `v-model` on child components: check for Vue 3 `v-model` changes (no `.sync`, use `modelValue` prop)

### `DaterangeSlider.vue` (126 lines) — MEDIUM effort

**Current:** Uses `vue2-datepicker` component.

**Migration plan:**
- Replace `vue2-datepicker` with `@vuepic/vue-datepicker`
- Update template bindings to match new component API
- Test date range selection behavior

### `CourseEditor.vue` (137 lines) — MEDIUM effort

**Current:** `beforeDestroy` lifecycle hook, Google Maps drawing manager.

**Migration plan:**
- Replace `beforeDestroy` → `onBeforeUnmount`
- Replace `this.$apollo.mutate()` → `useMutation()`
- Google Maps drawing API usage remains the same

### Other components — LOW effort

Most remaining components are simple and primarily need:
- Store access updated to Pinia
- `this.$apollo.mutate()` → `useMutation()`
- `this.$t()` → keep as-is in template (works in Vue 3)

---

## 14. Risk Assessment

### High Risk
| Risk | Mitigation |
|------|-----------|
| Google Maps integration breaks | Test early in Phase 2; Maps JS API is framework-agnostic |
| Apollo migration introduces query bugs | Test every GraphQL query individually; compare results |
| `@nuxtjs/apollo` alternative doesn't support all features | Manual Apollo setup gives full control |

### Medium Risk
| Risk | Mitigation |
|------|-----------|
| Third-party Vue 3 packages have different APIs | Research each replacement's API before migration |
| Touch/swipe behavior changes on mobile | Test thoroughly on real mobile devices |
| Bundle size increases | Monitor with `nuxi analyze`; Vite tree-shaking should help |
| Migration takes longer than estimated | Phase-based approach allows partial deployment |

### Low Risk
| Risk | Mitigation |
|------|-----------|
| Tailwind CSS incompatibility | Tailwind is framework-agnostic |
| i18n locale files need changes | JSON files are compatible; only config changes |
| Cypress tests break | Update selectors incrementally |

---

## 15. Decisions to Make

Before starting the migration, the following decisions should be made:

### 15.1 TypeScript adoption?
- **Option A:** Full TypeScript (recommended — Nuxt 4 has excellent TS support)
- **Option B:** JavaScript with JSDoc types
- **Option C:** Plain JavaScript (same as current)

### 15.2 Options API vs Composition API scope?
- **Option A:** Convert all components to `<script setup>` (cleanest, most work)
- **Option B:** Convert only complex components; keep simple ones as Options API (pragmatic)
- **Option C:** Keep all components as Options API (least work, but misses Composition API benefits)

### 15.3 Fresh project vs in-place upgrade?
- **Option A:** Fresh Nuxt 4 project in new directory (recommended — cleaner)
- **Option B:** In-place upgrade in existing `frontend/` directory

### 15.4 Directory structure?
- **Option A:** Replace `frontend/` with new Nuxt 4 code once ready
- **Option B:** Run both `frontend/` (Nuxt 2) and `frontend-v4/` (Nuxt 4) during migration

### 15.5 Datepicker replacement?
- **Option A:** `@vuepic/vue-datepicker` (most popular, feature-rich)
- **Option B:** `vue-datepicker-next` (closest API to vue2-datepicker)
- **Option C:** Custom date input with native browser datepicker

---

## Estimated Timeline

| Phase | Description | Estimated Duration |
|-------|-------------|-------------------|
| 0 | Preparation | 1 week |
| 1 | Project skeleton & config | 1 week |
| 2 | Core infrastructure (Apollo, i18n, auth, routing) | 2 weeks |
| 3 | Component migration (4 waves) | 3–4 weeks |
| 4 | State management (Vuex → Pinia) | 1 week |
| 5 | Plugin & middleware migration | 1 week |
| 6 | Third-party package replacements | 1–2 weeks |
| 7 | Testing, polish & deployment | 2 weeks |
| **Total** | | **~12 weeks** |

> **Note:** Phases 3, 4, 5, and 6 can overlap significantly since component migration often involves updating store access, plugins, and packages simultaneously. Realistic elapsed time: **8–10 weeks** with overlap.
