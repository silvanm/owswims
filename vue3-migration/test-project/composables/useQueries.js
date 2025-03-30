// No imports needed

export function useQueries() {
  // Mock data for location query
  const mockLocationData = {
    data: {
      id: 'location-1',
      city: 'Zurich',
      country: 'Switzerland',
      lat: 47.3474476,
      lng: 8.6733976,
      allEvents: {
        edges: [
          {
            node: {
              id: 'event-1',
              name: 'Zurich Swim',
              dateStart: new Date().toISOString(),
              website: 'https://example.com/zurich-swim',
              races: {
                edges: [
                  {
                    node: {
                      id: 'race-1',
                      distance: 1000,
                      coordinates: [
                        [47.3474476, 8.6733976],
                        [47.3474476, 8.6833976],
                        [47.3574476, 8.6833976],
                        [47.3574476, 8.6733976],
                        [47.3474476, 8.6733976],
                      ],
                    },
                  },
                ],
              },
            },
          },
        ],
      },
    },
  }

  // Mock function to simulate GraphQL query for location
  const location = (id, keyword, dateRange) => {
    // Log parameters to avoid unused variable warnings
    console.log(
      `Querying location with id: ${id}, keyword: ${keyword}, dateRange: ${dateRange}`
    )

    // Simulate async API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(mockLocationData)
      }, 100)
    })
  }

  // Mock function to simulate GraphQL query for events
  const events = (filters) => {
    // Log parameters to avoid unused variable warnings
    console.log(`Querying events with filters:`, filters)

    // Simulate async API call
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          data: {
            allEvents: {
              edges: mockLocationData.data.allEvents.edges,
            },
          },
        })
      }, 100)
    })
  }

  return {
    location,
    events,
  }
}
