export const state = () => ({
  lat: null,
  lng: null,
})

export const mutations = {
  mylocation(s, latlng) {
    s.lat = latlng.lat
    s.lng = latlng.lng
  },
}

export const getters = {
  mylocation(s) {
    return {
      lat: s.lat,
      lng: s.lng,
    }
  },
}
