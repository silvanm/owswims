export const state = () => ({
  lat: null,
  lng: null,
  pickedLocationId: null,
  distanceRange: [0, 30],
  dateRange: [0, 12],
})

export const mutations = {
  mylocation(s, latlng) {
    s.lat = latlng.lat
    s.lng = latlng.lng
  },
  pickedLocationId(s, id) {
    s.pickedLocationId = id
  },
  distanceRange(s, id) {
    s.distanceRange = id
  },
  dateRange(s, id) {
    s.dateRange = id
  },
}

export const getters = {
  mylocation(s) {
    return {
      lat: s.lat,
      lng: s.lng,
    }
  },
  pickedLocationId(s) {
    return s.pickedLocationId
  },
  distanceRange(s) {
    return s.distanceRange
  },
  dateRange(s) {
    return s.dateRange
  },
}
