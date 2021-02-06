import gql from 'graphql-tag'

export default async function ({ route, app, store }) {
  if (route.query.organizer) {
    const slug = route.query.organizer
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
        slug,
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
  if (route.query.event) {
    const slug = route.query.event
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
        slug,
      },
    })
    store.commit('focusedEventId', result.data.allEvents.edges[0].node)
    store.commit(
      'pickedLocationZoomedIn',
      result.data.allEvents.edges[0].node.location.id
    )
    // this.openLocation(result.data.allEvents.edges[0].node.location.id);
  }
}
