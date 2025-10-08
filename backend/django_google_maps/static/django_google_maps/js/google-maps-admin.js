/*
Integration for Google Maps in the django admin. 2

How it works:

You have an address field on the page.
Enter an address and an on change event will update the map
with the address. A marker will be placed at the address.
If the user needs to move the marker, they can and the geolocation
field will be updated.

Only one marker will remain present on the map at a time.

This script expects:

<input type="text" name="address" id="id_address" />
<input type="text" name="geolocation" id="id_geolocation" />

<script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false"></script>

*/

function googleMapAdmin() {
  var placeAutocomplete;
  var geocoder;
  var map;
  var marker;

  var latId = "id_lat";
  var lngId = "id_lng";
  var addressId = "id_address";
  var countryId = "id_country";
  var cityId = "id_city";

  var self = {
    initialize: function () {
      // Initialize geocoder
      geocoder = new google.maps.Geocoder();

      var lat = 0;
      var lng = 0;
      var zoom = 2;
      // set up initial map to be world view. also, add change
      // event so changing address will update the map
      var existinglocation = self.getExistingLocation();

      if (existinglocation) {
        lat = existinglocation[0];
        lng = existinglocation[1];
        zoom = 18;
      }

      var city = document.getElementById(cityId).value;
      var e = document.getElementById(countryId);
      var country = e.options[e.selectedIndex].text;
      var addressField = document.getElementById(addressId);

      if (addressField.value === "") {
        if (city && country) {
          addressField.value = `${city}, ${country}`;
        } else {
          addressField.value = country;
        }
      }

      var latlng = new google.maps.LatLng(lat, lng);
      var myOptions = {
        zoom: zoom,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.HYBRID,
      };
      map = new google.maps.Map(
        document.getElementById("map_canvas"),
        myOptions
      );
      if (existinglocation) {
        self.setMarker(latlng);
      }

      // Use the old but working Autocomplete API
      // Note: This will show a deprecation warning but is functional
      var autocomplete = new google.maps.places.Autocomplete(addressField);

      // Set types to get all place types
      autocomplete.setFields(['geometry', 'formatted_address', 'name', 'photos', 'place_id']);

      console.log("Autocomplete created for addressField");

      // Listen for place_changed event (old API)
      autocomplete.addListener('place_changed', function() {
        console.log("place_changed event fired!");
        var place = autocomplete.getPlace();
        console.log("Place object:", place);

        if (!place.geometry) {
          console.log("No geometry found, using geocoder fallback");
          // User entered a name that was not a suggestion
          self.codeAddress(place);
          return;
        }

        // Place has geometry
        console.log("Place has geometry:", place.geometry.location);
        self.codeAddress(place);
      });

      // don't make enter submit the form, let it just trigger the place selection
      $("#" + addressId).keydown(function (e) {
        if (e.keyCode == 13) {
          // enter key
          e.preventDefault();
          return false;
        }
      });
    },

    getExistingLocation: function () {
      var lat = document.getElementById(latId).value;
      var lng = document.getElementById(lngId).value;
      return [lat, lng];
    },

    codeAddress: function (place) {
      if (!place) {
        console.log("No place provided to codeAddress");
        return;
      }

      console.log("Processing place in codeAddress:", place);

      // Display photos if available
      if (place.photos && place.photos.length > 0) {
        self.displayPhotos(place.photos);
      }

      // Old Autocomplete API uses 'geometry.location'
      if (place.geometry && place.geometry.location) {
        console.log("Found location from geometry:", place.geometry.location);
        self.updateWithCoordinates(place.geometry.location);
      } else {
        // Fallback to geocoding if no direct coordinates
        const address = place.formatted_address || place.name;
        console.log("No geometry found, geocoding address:", address);
        if (address) {
          geocoder.geocode({ address: address }, function (results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
              var latlng = results[0].geometry.location;
              self.updateWithCoordinates(latlng);
            } else {
              alert(
                "Geocode was not successful for the following reason: " + status
              );
            }
          });
        }
      }
    },

    updateWithCoordinates: function (latlng) {
      map.setCenter(latlng);
      map.setZoom(18);
      self.setMarker(latlng);
      self.updateGeolocation(latlng);
    },

    setMarker: function (latlng) {
      if (marker) {
        self.updateMarker(latlng);
      } else {
        self.addMarker({ latlng: latlng, draggable: true });
      }
    },

    addMarker: function (Options) {
      marker = new google.maps.Marker({
        map: map,
        position: Options.latlng,
      });

      var draggable = Options.draggable || false;
      if (draggable) {
        self.addMarkerDrag(marker);
      }
    },

    addMarkerDrag: function () {
      marker.setDraggable(true);
      google.maps.event.addListener(marker, "dragend", function (new_location) {
        self.updateGeolocation(new_location.latLng);
      });
    },

    updateMarker: function (latlng) {
      marker.setPosition(latlng);
    },

    updateGeolocation: function (latlng) {
      document.getElementById(latId).value = latlng.lat();
      document.getElementById(lngId).value = latlng.lng();
      $("#" + latId).trigger("change");
    },

    displayPhotos: function (photos) {
      document.getElementById("photos").innerHTML = "";
      if (!photos || photos.length === 0) {
        return;
      }

      photos.forEach((photo) => {
        var div = document.createElement("div");
        let src;

        // Handle both old API (photo.getUrl) and new API (photo.getURI)
        if (typeof photo.getUrl === 'function') {
          src = photo.getUrl({ maxWidth: 600, maxHeight: 600 });
        } else if (typeof photo.getURI === 'function') {
          src = photo.getURI({ maxWidth: 600, maxHeight: 600 });
        } else if (photo.url) {
          src = photo.url;
        } else {
          return; // Skip if we can't get a URL
        }

        div.style = `background-image: url(${src})`;
        div.className = "places-photo";
        document.getElementById("photos").appendChild(div);
        div.addEventListener("click", (e) => {
          console.log(src);
          document.getElementById("id_temp_image_url").value = src;
        });
      });
    },
  };

  return self;
}

// Global callback function for Google Maps API
function initGoogleMapsAdmin() {
  $(document).ready(function () {
    var googlemap = googleMapAdmin();
    googlemap.initialize();
  });
}
