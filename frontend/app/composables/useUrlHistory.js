/**
 * Composable replacing the old this.$urlHistory plugin.
 * Pushes query parameters to the browser URL without triggering a Vue Router navigation.
 */
export function useUrlHistory() {
  const { locale } = useI18n()

  function encodeQueryData(data) {
    const ret = []
    for (const d in data) {
      ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]))
    }
    return ret.join('&')
  }

  function push(query = {}, path = null) {
    if (typeof window === 'undefined') return

    const route = useRoute()

    if (path !== null) {
      path = '/' + locale.value + path
    } else {
      path = window.location.pathname
    }

    const queryVar = { ...route.query, ...query }

    // The reason we don't do this via the router engine of Nuxt is because
    // pushing a new route to the router triggers a page rerender
    history.pushState({}, '', path + '?' + encodeQueryData(queryVar))
  }

  // Handle browser back/forward for /info/<tab> URLs
  if (import.meta.client) {
    const store = useMainStore()
    window.addEventListener('popstate', () => {
      const infoMatch = window.location.pathname.match(
        /\/info\/(help|organizers|contributors|imprint)\/?$/
      )
      if (infoMatch) {
        store.activeInfoTab = infoMatch[1]
      } else {
        store.activeInfoTab = null
      }
    })
  }

  return {
    push,
  }
}
