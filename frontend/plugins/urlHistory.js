function encodeQueryData(data) {
  const ret = []
  for (const d in data)
    ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]))
  return ret.join('&')
}

export default ({ app, store }, inject) => {
  inject('urlHistory', {
    push(query = {}, path = null) {
      if (path !== null) {
        path = '/' + app.i18n.locale + path
      } else {
        path = window.location.pathname
      }

      const queryVar = { ...app.router.currentRoute.query, ...query }

      // The reason we don't do this via the router engine of Nuxt, is because
      // pushing a new route to the router triggers a page rerender
      history.pushState({}, '', path + '?' + encodeQueryData(queryVar))
    },
  })

  // Handle browser back/forward for /info/<tab> URLs
  if (process.client) {
    window.addEventListener('popstate', () => {
      const infoMatch = window.location.pathname.match(
        /\/info\/(help|organizers|contributors|imprint)\/?$/
      )
      if (infoMatch) {
        store.commit('activeInfoTab', infoMatch[1])
      } else {
        store.commit('activeInfoTab', null)
      }
    })
  }
}
