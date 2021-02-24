import gql from 'graphql-tag'

export default async function ({ route, app, store }) {
  function getOrganizerFromRequest() {
    const re = /\/organizer\/([^/]+)$/
    const m = route.path.match(re)
    if (m && m[1]) {
      return m[1]
    } else if (route.query.organizer) {
      return route.query.organizer
    }
  }

  const organizerSlug = getOrganizerFromRequest()
  if (organizerSlug) {
    const client = app.apolloProvider.defaultClient
    const result = await client.query({
      query: gql`
        query($slug: String!) {
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
    store.commit('organizerData', result.data.allOrganizers.edges[0].node)
  }
  if (route.query.embedded) {
    store.commit('isEmbedded', true)
  }
  if (route.query.map_type) {
    store.commit('mapType', route.query.map_type)
  }
  if (route.query.show_organizer_logo) {
    store.commit('showOrganizerLogo', route.query.show_organizer_logo === '1')
  }

  function getEventFromRequest() {
    const re = /\/event\/([^/]+)$/
    const m = route.path.match(re)
    if (m && m[1]) {
      return m[1]
    } else if (route.query.event) {
      return route.query.event
    }
  }

  // add function to disable event-pane + define zoom level
  const eventSlug = getEventFromRequest()
  if (eventSlug) {
    const client = app.apolloProvider.defaultClient
    const result = await client.query({
      query: gql`
        query($slug: String!) {
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
    store.commit(
      'pickedLocationZoomedIn',
      result.data.allEvents.edges[0].node.location.id
    )
    // this.openLocation(result.data.allEvents.edges[0].node.location.id);
  }
}
