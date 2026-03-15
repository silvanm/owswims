import gql from 'graphql-tag'

export default defineNuxtRouteMiddleware(async (to, from) => {
  const store = useMainStore()
  const { $apollo } = useNuxtApp()

  function getOrganizerFromRequest() {
    const re = /\/organizer\/([^/]+)\/?$/
    const m = to.path.match(re)
    if (m && m[1]) {
      return m[1]
    } else if (to.query.organizer) {
      return to.query.organizer as string
    }
  }

  const organizerSlug = getOrganizerFromRequest()
  if (organizerSlug) {
    const result = await $apollo.query({
      query: gql`
        query ($slug: String!) {
          allOrganizers(slug: $slug) {
            edges {
              node {
                id
                website
                logo
                slug
                name
              }
            }
          }
        }
      `,
      variables: {
        slug: organizerSlug,
      },
    })
    const edges = result.data.allOrganizers.edges
    if (edges && edges.length > 0) {
      store.organizerData = edges[0].node
    }
  }

  if (to.query.embedded) {
    store.isEmbedded = true
  }
  if (to.query.map_type) {
    store.mapType = to.query.map_type as string
  }
  if (to.query.show_organizer_logo) {
    store.showOrganizerLogo = to.query.show_organizer_logo === '1'
  }

  function getEventFromRequest() {
    const re = /.*\/event\/([^/]+)\/?$/
    const m = to.path.match(re)
    if (m && m[1]) {
      return m[1]
    } else if (to.query.event) {
      return to.query.event as string
    }
  }

  // Handle /submit path to open submit event modal
  const submitMatch = to.path.match(/\/submit\/?$/)
  if (submitMatch) {
    store.submitEventBoxShown = true
  }

  // Handle /info/<tab> path to open info pane with specific tab
  const infoMatch = to.path.match(
    /\/info\/(help|organizers|contributors|imprint|partners)\/?$/
  )
  if (infoMatch) {
    store.activeInfoTab = infoMatch[1]
  }

  // add function to disable event-pane + define zoom level
  const eventSlug = getEventFromRequest()
  if (eventSlug) {
    const result = await $apollo.query({
      query: gql`
        query ($slug: String!) {
          allEvents(slug: $slug) {
            edges {
              node {
                id
                location {
                  id
                }
              }
            }
          }
        }
      `,
      variables: {
        slug: eventSlug,
      },
    })
    const edges = result.data.allEvents.edges
    if (edges && edges.length > 0) {
      store.pickedLocationZoomedIn = edges[0].node.location.id
    }
  }
})
