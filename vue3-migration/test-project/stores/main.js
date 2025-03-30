// stores/main.js
import { defineStore } from 'pinia'
import { addMonths } from 'date-fns'

// Mock data for testing the EventPane component
const mockLocationData = {
  location: {
    id: 'TG9jYXRpb246MQ==',
    city: 'Zurich',
    country: 'Switzerland',
    waterName: 'Lake Zurich',
    headerPhoto: 'https://picsum.photos/800/400',
    lat: 47.3769,
    lng: 8.5417,
    waterType: 'LAKE',
  },
  allEvents: {
    edges: [
      {
        node: {
          id: 'RXZlbnQ6MQ==',
          name: 'Zurich Lake Swim',
          slug: 'zurich-lake-swim-2025',
          dateStart: '2025-07-15',
          website: 'https://example.com/event',
          description: 'A beautiful open water swimming event in Lake Zurich.',
          flyerImage: 'https://picsum.photos/600/800',
          soldOut: false,
          cancelled: false,
          needsMedicalCertificate: true,
          needsLicense: false,
          withRanking: true,
          waterTemp: 22,
          organizer: {
            name: 'Zurich Swimming Club',
            website: 'https://example.com/organizer',
            logo: 'https://picsum.photos/200/100',
          },
          reviews: {
            edges: [
              {
                node: {
                  id: 'UmV2aWV3OjE=',
                  rating: 4.5,
                  comment: 'Great event, well organized!',
                  createdAt: '2024-12-01T12:00:00Z',
                  country: 'CH',
                  name: 'John Doe',
                },
              },
            ],
          },
          races: {
            edges: [
              {
                node: {
                  id: 'UmFjZTox',
                  name: 'Short Distance',
                  date: '2025-07-15',
                  raceTime: '09:00:00',
                  distance: 1.5,
                  wetsuit: 'OPTIONAL',
                  priceValue: '50',
                  priceCurrency: 'CHF',
                  coordinates: 'LINESTRING(8.5417 47.3769, 8.5517 47.3869)',
                },
              },
              {
                node: {
                  id: 'UmFjZToy',
                  name: 'Long Distance',
                  date: '2025-07-15',
                  raceTime: '11:00:00',
                  distance: 3.0,
                  wetsuit: 'OPTIONAL',
                  priceValue: '80',
                  priceCurrency: 'CHF',
                  coordinates: 'LINESTRING(8.5417 47.3769, 8.5617 47.3969)',
                },
              },
            ],
          },
        },
      },
    ],
  },
  node: {
    waterType: 'LAKE',
  },
}

export const useMainStore = defineStore('main', {
  state: () => ({
    lat: 47.3769,
    lng: 8.5417,
    isAccurate: true,
    countryCode: 'CH',
    pickedLocationId: 'TG9jYXRpb246MQ==',
    pickedLocationZoomedIn: null,
    keyword: '',
    organizerData: null,
    isEmbedded: false,
    mapType: false,
    showOrganizerLogo: false,
    distanceRange: [0, 1000],
    dateRange: [new Date(), addMonths(new Date(), 12)],
    pickedLocationData: mockLocationData,
    focusedEventId: null,
    travelTimes: {
      '47.3769,8.5417': {
        duration: 1800, // 30 minutes in seconds
        distance: 25000, // 25km in meters
      },
    },
    isLoading: false,
    justMounted: false,
    raceTrackUnderEditId: null,
    raceTrackUnderFocusId: null,
    raceTrackUnderHoverId: null,
    raceTrackDeletedId: null,
    pageTitle: null,
    reviewBoxShown: false,
    mylocation: {
      isAccurate: true,
      latlng: {
        lat: 47.3769,
        lng: 8.5417,
      },
    },
  }),

  // In Pinia, you don't need getters that just return state properties
  // They are automatically available as properties of the store

  actions: {
    setPickedLocationZoomedIn(data) {
      this.pickedLocationZoomedIn = data
    },
    setFocusedEventId(data) {
      this.focusedEventId = data
    },
    setRaceTrackUnderEditId(id) {
      this.raceTrackUnderEditId = id
    },
    setRaceTrackUnderFocusId(id) {
      this.raceTrackUnderFocusId = id
    },
    setRaceTrackUnderHoverId(id) {
      this.raceTrackUnderHoverId = id
    },
    setReviewBoxShown(shown) {
      this.reviewBoxShown = shown
    },
  },
})
