export const state = () => ({
  lat: null,
  lng: null,
  pickedLocationId: null,
})

export const mutations = {
  mylocation(s, latlng) {
    s.lat = latlng.lat
    s.lng = latlng.lng
  },
  pickedLocationId(s, id) {
    s.pickedLocationId = id
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
}
