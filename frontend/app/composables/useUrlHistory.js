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

  function getCurrentQuery() {
    if (typeof window === 'undefined') return {}
    const search = window.location.search
    if (!search || search === '?') return {}
    const params = new URLSearchParams(search)
    const obj = {}
    for (const [key, value] of params.entries()) {
      obj[key] = value
    }
    return obj
  }

  function push(query = {}, path = null) {
    if (typeof window === 'undefined') return

    if (path !== null) {
      path = '/' + locale.value + path
    } else {
      path = window.location.pathname
    }

    // Use current URL query so params set via pushState are preserved (router is not updated by pushState)
    const queryVar = { ...getCurrentQuery(), ...query }

    // The reason we don't do this via the router engine of Nuxt is because
    // pushing a new route to the router triggers a page rerender
    const search = encodeQueryData(queryVar)
    history.pushState({}, '', search ? path + '?' + search : path)
  }

  // Handle browser back/forward for /info/<tab> URLs
  if (import.meta.client) {
    const store = useMainStore()
    window.addEventListener('popstate', () => {
      const infoMatch = window.location.pathname.match(
        /\/info\/(help|organizers|contributors|imprint|partners)\/?$/
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
