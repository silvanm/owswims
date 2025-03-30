import { inject } from 'vue'

export function useI18n() {
  // Get the i18n object from the plugin
  const i18n = inject('i18n')

  if (!i18n) {
    console.error('i18n plugin not found')

    // Provide a fallback if i18n is not available
    return {
      locale: 'en',
      t: (key) => key,
    }
  }

  return {
    locale: i18n.locale,
    t: (key) => i18n.t(key),
  }
}
