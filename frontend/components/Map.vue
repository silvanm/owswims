<template>
  <div>
    <div ref="eventDescription">
      <div v-if="pickedEvent">
        <h1 class="text-xl font-semibold">
          {{ pickedEvent.city }}, {{ pickedEvent.country }}
        </h1>
        <span v-if="mylocation.lat">
          Travel time: {{ getFormattedTravelDistance(pickedEvent, 'DRIVING') }}
        </span>
        <div v-for="event in pickedEvent.events.edges" :key="event.node.id">
          <div style="margin-top: 10px">
            {{ formatEventDate(event.node.dateStart) }}<br />
            <a :href="event.node.website" class="font-semibold">{{
              event.node.name
            }}</a
            ><br />
            {{ formatRaceDistances(event.node.races) }}
          </div>
        </div>
      </div>
    </div>
    <div id="map"></div>
  </div>
</template>
<script>
import MarkerClusterer from '@googlemaps/markerclustererplus'
import { addMonths, format, formatDistance, formatISO } from 'date-fns'
import { mapGetters } from 'vuex'
import gql from 'graphql-tag'

export default {
  apollo: {
    allEvents: {
      query: gql`
        query(
          $distanceFrom: Float!
          $distanceTo: Float!
          $dateFrom: Date!
          $dateTo: Date!
          $locationId: ID!
        ) {
          allEvents(
            dateFrom: $dateFrom
            dateTo: $dateTo
            location: $locationId
          ) {
            edges {
              node {
                id
                name
                dateStart
                dateEnd
                website
                races(distance_Gte: $distanceFrom, distance_Lte: $distanceTo) {
                  edges {
                    node {
                      distance
                    }
                  }
                }
              }
            }
          }
        }
      `,
      variables() {
        return {
          locationId: this.pickedLocationId,
          distanceFrom: this.distanceFrom,
          distanceTo: this.distanceTo,
          dateFrom: formatISO(addMonths(new Date(), this.dateRange[0]), {
            representation: 'date',
          }),
          dateTo: formatISO(addMonths(new Date(), this.dateRange[1]), {
            representation: 'date',
          }),
        }
      },
      watchLoading(isLoading, countModifier) {
        this.isLoading = isLoading
      },
    },
  },
  props: {
    google: {
      type: Object,
      default: null,
    },
    locations: {
      type: Array,
      default: () => {
        return []
      },
    },
    distanceFrom: {
      type: Number,
      default: () => {
        return 0
      },
    },
    distanceTo: {
      type: Number,
      default: () => {
        return 100
      },
    },
    dateRange: {
      type: Array,
      default: () => {
        return [-10, 10]
      },
    },
  },
  data() {
    return {
      marker: {},
      pickedLocationId: 'TG9jYXRpb25Ob2RlOjE4NTg=',
      pickedLocation: null,
      // Stores travel times per location (null == not possible to fetch)
      travelTimes: {},
      formattedTravelDistance: '',
      isLoading: false,
    }
  },
  computed: {
    ...mapGetters(['mylocation']),
  },
  watch: {
    locations(newlocations, oldlocations) {
      this.updateMarker()
    },
    mylocation(newLocation, oldLocation) {
      if (newLocation.lat && newLocation.lng) {
        const icon = {
          path:
            'M 25, 50\n' +
            '    a 25,25 0 1,1 50,0\n' +
            '    a 25,25 0 1,1 -50,0',
          fillColor: '#4299E1',
          fillOpacity: 1,
          anchor: new this.google.maps.Point(0, 0),
          strokeWeight: 1,
          strokeColor: '#fff',
          scale: 0.25,
        }
        this.myLocationMarker = new this.google.maps.Marker({
          icon,
          position: newLocation,
          map: this.map,
        })
      }
    },
  },
  mounted() {
    this.map = new this.google.maps.Map(document.getElementById('map'), {
      center: { lat: 47.3474476, lng: 8.6733976 },
      zoom: 5,
      disableDefaultUI: false,
      mapTypeId: 'satellite',
      mapTypeControl: false,
    })
    this.updateMarker()
  },
  methods: {
    markerPin() {
      return {
        path:
          'M66.9,41.8c0-11.3-9.1-20.4-20.4-20.4c-11.3,0-20.4,9.1-20.4,20.4c0,11.3,20.4,32.4,20.4,32.4S66.9,53.1,66.9,41.8z    M37,41.4c0-5.2,4.3-9.5,9.5-9.5c5.2,0,9.5,4.2,9.5,9.5c0,5.2-4.2,9.5-9.5,9.5C41.3,50.9,37,46.6,37,41.4z',
        fillColor: '#fff',
        fillOpacity: 1,
        anchor: new this.google.maps.Point(50, 70),
        strokeWeight: 0,
        scale: 0.7,
      }
    },
    centerMap() {
      if (this.lat && this.lng) {
        const myLatLng = new this.google.maps.LatLng(
          this.mylocation.lat,
          this.mylocation.lng
        )
        this.map.panTo(myLatLng)
      }
    },
    formatEventDate(dt) {
      return format(new Date(dt), 'E dd. MMM. yyyy')
    },
    formatRaceDistances(races) {
      function humanizeDistance(d) {
        if (d <= 1.5) {
          return (d * 1000).toFixed(0) + 'm'
        } else {
          return d.toFixed(0) + 'km'
        }
      }

      return races.edges
        .map((e) => humanizeDistance(e.node.distance))
        .join(', ')
    },
    getFormattedTravelDistance(location, travelMode) {
      console.log('getFormattedTravelDistance', location)
      const k = `${location.lat},${location.lng}`
      if (k in this.travelTimes && this.travelTimes[k][travelMode] !== null) {
        const formatDuration = (s) => formatDistance(0, s * 1000)

        return `${formatDuration(this.travelTimes[k][travelMode].duration)} (${(
          this.travelTimes[k][travelMode].distance / 1000
        ).toFixed(0)}km)`
      } else {
        return '?'
      }
    },
    updateMarker() {
      const infowindow = new this.google.maps.InfoWindow({
        content: this.$refs.eventDescription,
        fontFamily: "'Source Sans Pro', sans-serif",
      })

      if (this.markerCluster) {
        this.markerCluster.clearMarkers()
      }

      for (const id of Object.keys(this.marker)) {
        this.marker[id].setMap(null)
        delete this.marker[id]
      }

      for (const location of this.locations) {
        if (!(location.lat && location.lng)) {
          // latLng is mandatory
          continue
        }

        const markerObj = new this.google.maps.Marker({
          icon: this.markerPin(),
          position: location,
          map: this.map,
          title: location.name,
        })

        markerObj.addListener('click', () => {
          this.$store.commit('pickedLocationId', location.id)
          this.pickedLocationId = location.id
          this.pickedLocation = location
          this.location = location
          this.markerObj = markerObj
          console.log('Marker object click')
          infowindow.close()
          this.calculateDistance(this.location, () => {
            console.log('Distance calculated callback')
            infowindow.open(this.map, this.markerObj)
          })
        })
        this.marker[location.id] = markerObj
      }
      this.markerCluster = new MarkerClusterer(this.map, this.marker, {
        styles: [
          {
            width: 30,
            height: 30,
            className: 'custom-clustericon-1',
          },
          {
            width: 40,
            height: 40,
            className: 'custom-clustericon-2',
          },
          {
            width: 50,
            height: 50,
            className: 'custom-clustericon-3',
          },
        ],
        clusterClass: 'custom-clustericon',
      })
    },
    calculateDistance(location, callback) {
      const requestedDestinations = []
      // Calculate distance for those destinations within the viewport.
      const k = `${location.lat},${location.lng}`
      if (!(k in this.travelTimes)) {
        requestedDestinations.push(k)
      }

      const service = new this.google.maps.DistanceMatrixService()

      const travelModes = [this.google.maps.TravelMode.DRIVING]

      if (requestedDestinations.length === 0) callback()

      const promises = travelModes.map((travelMode) => {
        // Using DistanceMatrix for a 1x1 matrix is a bit pointless. But
        // I think the directions service is a bit too heavy for this kind of task.
        return service.getDistanceMatrix({
          origins: [
            new this.google.maps.LatLng(
              this.mylocation.lat,
              this.mylocation.lng
            ),
          ],
          destinations: [k],
          transitOptions: {
            // @todo: Is a hardcoded year really good here?
            departureTime: new Date(2020, 8, 2, 8, 0, 0),
          },
          travelMode,
          unitSystem: this.google.maps.UnitSystem.METRIC,
        })
      })

      // @todo simplify this
      Promise.all(promises).then((values) => {
        values.forEach((value, ix) => {
          const results = value.rows[0].elements
          console.log('Got distancematrix result', results)
          for (let j = 0; j < results.length; j++) {
            if (!this.travelTimes[requestedDestinations[j]]) {
              this.travelTimes[requestedDestinations[j]] = {
                DRIVING: null,
                TRANSIT: null,
              }
            }

            if (results[j].status === 'OK') {
              this.travelTimes[requestedDestinations[j]][travelModes[ix]] = {
                distance: results[j].distance.value,
                duration: results[j].duration.value,
              }
            } else {
              this.travelTimes[requestedDestinations[j]][travelModes[ix]] = null
            }
          }
        })
        this.formattedTravelDistance = this.getFormattedTravelDistance(
          location,
          'DRIVING'
        )

        callback()
      })
    },
  },
}
</script>

<style>
html,
body {
  height: 100%;
  width: 100%;
}

#map {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.gm-style .gm-style-iw {
  font-family: 'Source Sans Pro', sans-serif;
}

.gm-style .gm-style-iw-c {
  border-radius: 0;
}

.gm-style a {
  color: #4299e1;
}

.custom-clustericon {
  background: var(--cluster-color);
  color: #fff;
  border-radius: 100%;
  font-weight: bold;
  font-size: 15px;
  display: flex;
  align-items: center;
}

.custom-clustericon::before,
.custom-clustericon::after {
  content: '';
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;

  transform: translate(-50%, -50%);
  top: 50%;
  left: 50%;
  background: var(--cluster-color);
  opacity: 0.2;
  border-radius: 100%;
}

.custom-clustericon::before {
  padding: 7px;
}

.custom-clustericon::after {
  padding: 14px;
}

.custom-clustericon-1,
.custom-clustericon-2,
.custom-clustericon-3 {
  --cluster-color: #4299e1;
}
</style>
