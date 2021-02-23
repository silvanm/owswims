function encodeQueryData(data) {
  const ret = []
  for (const d in data)
    ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]))
  return ret.join('&')
}

export default ({ app }, inject) => {
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
}
