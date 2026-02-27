const calculateDistance = function (
  google,
  location,
  store,
  callback = () => {}
) {
  const requestedDestinations = []
  // Calculate distance for those destinations within the viewport.
  const k = `${location.lat},${location.lng}`
  if (!(k in store.getters.travelTimes)) {
    requestedDestinations.push(k)
  }

  const travelTimes = store.getters.travelTimes
  const service = new google.maps.DistanceMatrixService()
  const travelModes = [google.maps.TravelMode.DRIVING]

  if (requestedDestinations.length === 0) {
    callback()
  }

  // only calculate if we have position via browser - and not via IP
  if (!store.getters.mylocation.isAccurate) {
    callback()
  }

  // this would allow calculating travel distance for both driving and train
  const promises = travelModes.map((travelMode) => {
    // Using DistanceMatrix for a 1x1 matrix is a bit pointless. But
    // I think the directions service is a bit too heavy for this kind of task.
    return service.getDistanceMatrix({
      origins: [store.getters.mylocation.latlng],
      destinations: [k],
      transitOptions: {
        // @todo: Is a hardcoded year really good here?
        departureTime: new Date(2020, 8, 2, 8, 0, 0),
      },
      travelMode,
      unitSystem: google.maps.UnitSystem.METRIC,
    })
  })

  // @todo simplify this
  Promise.all(promises).then((values) => {
    values.forEach((value, ix) => {
      const results = value.rows[0].elements
      for (let j = 0; j < results.length; j++) {
        if (!travelTimes[requestedDestinations[j]]) {
          travelTimes[requestedDestinations[j]] = {
            DRIVING: null,
            TRANSIT: null,
          }
        }

        if (results[j].status === 'OK') {
          travelTimes[requestedDestinations[j]] = {
            distance: results[j].distance.value,
            duration: results[j].duration.value,
          }
        } else {
          travelTimes[requestedDestinations[j]][travelModes[ix]] = null
        }
      }
    })
    store.commit('travelTimes', travelTimes)
    callback()
  })
}

export default calculateDistance
