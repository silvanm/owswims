// Mock Google Maps API for testing purposes
export default defineNuxtPlugin(() => {
  // Create a mock Google Maps API
  const mockGoogleMaps = {
    maps: {
      Map: class Map {
        constructor(element, options) {
          this.element = element
          this.options = options
          this.center = options.center
          this.zoom = options.zoom
          this.controls = {
            TOP_RIGHT: [],
            RIGHT: [],
            BOTTOM_CENTER: [],
          }
          this.listeners = {}
          console.log('Google Maps initialized with center:', this.center)
        }

        setCenter(latLng) {
          this.center = latLng
          console.log('Map center set to:', latLng)
        }

        setZoom(zoom) {
          this.zoom = zoom
          console.log('Map zoom set to:', zoom)
        }

        getCenter() {
          return {
            lat: () => this.center.lat,
            lng: () => this.center.lng,
          }
        }

        getZoom() {
          return this.zoom
        }

        getBounds() {
          return {
            contains: () => true,
          }
        }

        fitBounds(bounds, padding) {
          console.log('Map fit to bounds with padding:', padding)
        }

        addListener(event, callback) {
          this.listeners[event] = callback
          return { remove: () => delete this.listeners[event] }
        }
      },

      Marker: class Marker {
        constructor(options) {
          this.position = options.position
          this.map = options.map
          this.title = options.title
          this.icon = options.icon
          this.listeners = {}
          console.log('Marker created at:', this.position)
        }

        setMap(map) {
          this.map = map
        }

        getPosition() {
          return {
            lat: () => this.position.lat,
            lng: () => this.position.lng,
          }
        }

        addListener(event, callback) {
          this.listeners[event] = callback
          return { remove: () => delete this.listeners[event] }
        }

        setOptions(options) {
          Object.assign(this, options)
        }

        setVisible(visible) {
          this.visible = visible
        }
      },

      InfoWindow: class InfoWindow {
        constructor(options) {
          this.content = options.content
          this.pixelOffset = options.pixelOffset
          console.log('InfoWindow created')
        }

        open(map, marker) {
          this.map = map
          this.marker = marker
          console.log('InfoWindow opened')
        }

        close() {
          console.log('InfoWindow closed')
        }
      },

      LatLng: class LatLng {
        constructor(lat, lng) {
          this.lat = lat
          this.lng = lng
        }

        lat() {
          return this.lat
        }

        lng() {
          return this.lng
        }
      },

      LatLngBounds: class LatLngBounds {
        constructor() {
          this.bounds = []
        }

        extend(latLng) {
          this.bounds.push(latLng)
          return this
        }
      },

      Size: class Size {
        constructor(width, height) {
          this.width = width
          this.height = height
        }
      },

      Point: class Point {
        constructor(x, y) {
          this.x = x
          this.y = y
        }
      },

      Polyline: class Polyline {
        constructor(options) {
          this.options = options
          this.path = options.path
          this.map = null
          console.log('Polyline created with', options.path.length, 'points')
        }

        setMap(map) {
          this.map = map
        }

        setOptions(options) {
          Object.assign(this.options, options)
        }

        getPath() {
          return {
            forEach: (callback) => {
              this.path.forEach((point, index) => {
                callback(
                  {
                    lat: () => point.lat,
                    lng: () => point.lng,
                  },
                  index
                )
              })
            },
          }
        }
      },

      MapTypeId: {
        ROADMAP: 'roadmap',
        SATELLITE: 'satellite',
        HYBRID: 'hybrid',
        TERRAIN: 'terrain',
      },

      ControlPosition: {
        TOP_RIGHT: 'TOP_RIGHT',
        RIGHT: 'RIGHT',
        BOTTOM_CENTER: 'BOTTOM_CENTER',
      },

      MapTypeControlStyle: {
        HORIZONTAL_BAR: 'HORIZONTAL_BAR',
      },

      SymbolPath: {
        FORWARD_CLOSED_ARROW: 'forward_closed_arrow',
      },
    },
  }

  // Add the mock to the window object
  if (import.meta.client) {
    window.google = mockGoogleMaps
    window.MarkerClusterer = class MarkerClusterer {
      constructor(map, markers, options) {
        this.map = map
        this.markers = markers
        this.options = options
        console.log('MarkerClusterer created with', markers.length, 'markers')
      }

      clearMarkers() {
        this.markers = []
        console.log('MarkerClusterer cleared')
      }
    }

    console.log('Google Maps API mock initialized')
  }
})
