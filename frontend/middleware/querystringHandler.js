import gql from 'graphql-tag'

export default async function ({ route, app, store }) {
  if (route.query.organization_id) {
    store.commit('organizationId', route.query.organization_id)
  }
  if (route.query.embedded) {
    store.commit('isEmbedded', true)
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
