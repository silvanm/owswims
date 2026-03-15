/**
 * E2E test target: fetches one locationId and eventSlug from GraphQL
 * so tests can run against any environment with data (no hardcoded slug).
 */

const GRAPHQL_URL =
  process.env.E2E_GRAPHQL_URL ??
  process.env.GRAPHQL_ENDPOINT ??
  'http://localhost:8000/graphql'

function defaultDateRange(): { dateFrom: string; dateTo: string } {
  const now = new Date()
  const dateFrom = now.toISOString().split('T')[0]
  const to = new Date(now.getFullYear(), now.getMonth() + 12, now.getDate())
  const dateTo = to.toISOString().split('T')[0]
  return { dateFrom, dateTo }
}

export interface TestTarget {
  locationId: string
  eventSlug: string
}

// Origin expected by backend CORS/CSRF whitelist (so GraphQL POST is allowed without CSRF token)
const E2E_ORIGIN = process.env.E2E_ORIGIN ?? 'http://localhost:3000'

async function graphql<T>(query: string, variables: Record<string, unknown>): Promise<T> {
  const res = await fetch(GRAPHQL_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Origin: E2E_ORIGIN,
    },
    body: JSON.stringify({ query, variables }),
  })
  if (!res.ok) {
    throw new Error(`GraphQL ${res.status}: ${await res.text()}`)
  }
  const json = await res.json()
  if (json.errors?.length) {
    throw new Error(`GraphQL errors: ${JSON.stringify(json.errors)}`)
  }
  return json.data as T
}

const LOCATIONS_FILTERED = `
  query (
    $keyword: String!
    $distanceFrom: Float!
    $distanceTo: Float!
    $dateFrom: Date!
    $dateTo: Date!
    $organizerSlug: String!
    $organizerId: ID!
  ) {
    locationsFiltered(
      keyword: $keyword
      raceDistanceGte: $distanceFrom
      raceDistanceLte: $distanceTo
      dateFrom: $dateFrom
      dateTo: $dateTo
      organizerSlug: $organizerSlug
      organizerId: $organizerId
    ) {
      id
    }
  }
`

const LOCATION_AND_EVENTS = `
  query ($dateFrom: Date!, $dateTo: Date!, $locationId: ID!) {
    location(id: $locationId) {
      id
    }
    allEvents(dateFrom: $dateFrom, dateTo: $dateTo, location: $locationId) {
      edges {
        node {
          slug
        }
      }
    }
  }
`

/**
 * Returns one locationId and one eventSlug for E2E tests.
 * Uses E2E_LOCATION_ID / E2E_EVENT_SLUG if set (e.g. in CI with seeded data).
 */
export async function getTestTarget(): Promise<TestTarget> {
  const overrideLocationId = process.env.E2E_LOCATION_ID
  const overrideEventSlug = process.env.E2E_EVENT_SLUG
  if (overrideLocationId && overrideEventSlug) {
    return { locationId: overrideLocationId, eventSlug: overrideEventSlug }
  }

  const { dateFrom, dateTo } = defaultDateRange()

  const locationsData = await graphql<{ locationsFiltered: { id: string }[] }>(
    LOCATIONS_FILTERED,
    {
      keyword: '',
      distanceFrom: 0,
      distanceTo: 1000,
      dateFrom,
      dateTo,
      organizerSlug: '',
      organizerId: '',
    }
  )

  const locations = locationsData?.locationsFiltered
  if (!locations?.length) {
    throw new Error(
      'E2E: No events in default date range. Seed data or run against an env with data.'
    )
  }

  const locationId = overrideLocationId ?? locations[0].id

  const eventsData = await graphql<{
    location: { id: string }
    allEvents: { edges: { node: { slug: string } }[] }
  }>(LOCATION_AND_EVENTS, {
    locationId,
    dateFrom,
    dateTo,
  })

  const edges = eventsData?.allEvents?.edges
  const eventSlug =
    overrideEventSlug ?? edges?.[0]?.node?.slug
  if (!eventSlug) {
    throw new Error(
      `E2E: Location ${locationId} has no events in default date range.`
    )
  }

  return { locationId, eventSlug }
}
