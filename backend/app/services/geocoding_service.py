import logging
import math
from typing import List, Dict, Tuple, Optional, Any

from django.conf import settings
import googlemaps
import pycountry

from app.models import Location

logger = logging.getLogger(__name__)


class GeocodingService:
    """
    A shared service for geocoding operations throughout the application.
    Consolidates geocoding logic from multiple commands into a single service.
    """

    def __init__(self, api_key=None, stdout=None, stderr=None):
        """
        Initialize the geocoding service.

        Args:
            api_key: Google Maps API key (defaults to settings.GOOGLE_MAPS_API_KEY)
            stdout: Output stream for logging (optional)
            stderr: Error stream for logging (optional)
        """
        self.api_key = api_key or settings.GOOGLE_MAPS_API_KEY
        self.gmaps = googlemaps.Client(key=self.api_key)
        self.stdout = stdout
        self.stderr = stderr

    def _log(self, msg: str, level: str = "info", style_func=None):
        """Log a message to both the logger and command output if available"""
        # Log to Python logger
        getattr(logger, level)(msg)

        # Log to command output if available
        if level in ["warning", "error"] and self.stderr:
            if style_func:
                self.stderr.write(style_func(msg))
            else:
                self.stderr.write(msg)
        elif self.stdout:
            if style_func:
                self.stdout.write(style_func(msg))
            else:
                self.stdout.write(msg)

    def geocode_by_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Forward geocode an address to get coordinates.

        Args:
            address: The address to geocode

        Returns:
            Dictionary with geocoding results or None if geocoding failed
        """
        try:
            self._log(f"Geocoding address: {address}")
            geocode_result = self.gmaps.geocode(address)

            if geocode_result:
                self._log(f"Successfully geocoded: {address}")
                return geocode_result[0]
            else:
                self._log(f"No geocoding results for: {address}", "warning")
                return None

        except Exception as e:
            self._log(f"Geocoding error: {str(e)}", "error")
            return None

    def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """
        Reverse geocode coordinates to get address information.

        Args:
            lat: Latitude
            lng: Longitude

        Returns:
            Dictionary with reverse geocoding results or None if geocoding failed
        """
        try:
            self._log(f"Reverse geocoding coordinates: {lat}, {lng}")
            geocode_result = self.gmaps.reverse_geocode((lat, lng))

            if geocode_result:
                self._log(f"Successfully reverse geocoded: {lat}, {lng}")
                return geocode_result[0]
            else:
                self._log(f"No reverse geocoding results for: {lat}, {lng}", "warning")
                return None

        except Exception as e:
            self._log(f"Reverse geocoding error: {str(e)}", "error")
            return None

    def update_location_from_geocode_result(
        self, location: Location, geocode_result: Dict[str, Any]
    ) -> bool:
        """
        Update a Location object with data from a geocode result.

        Args:
            location: The Location object to update
            geocode_result: The geocoding result from Google Maps API

        Returns:
            True if the location was updated successfully, False otherwise
        """
        try:
            # Extract address components
            geocoded_address = {
                "street_number": "",
                "route": "",
                "locality": "",
                "postal_town": "",
                "country": "",
            }

            for component in geocode_result["address_components"]:
                for part in geocoded_address.keys():
                    if part in component["types"]:
                        geocoded_address[part] = (
                            component["long_name"]
                            if part != "country"
                            else component["short_name"]
                        )

            # Update location fields
            location.address = geocoded_address["route"]
            if geocoded_address["street_number"]:
                location.address += " " + geocoded_address["street_number"]

            location.city = (
                geocoded_address["locality"]
                if geocoded_address["locality"]
                else geocoded_address["postal_town"]
            )

            location.country = geocoded_address["country"]
            location.lat = geocode_result["geometry"]["location"]["lat"]
            location.lng = geocode_result["geometry"]["location"]["lng"]

            # Ensure address includes city and country
            if location.address and not location.address.endswith(location.country):
                if not location.address.endswith(location.city):
                    location.address += f", {location.city}"
                location.address += f", {location.country}"

            return True

        except Exception as e:
            self._log(f"Error updating location from geocode result: {str(e)}", "error")
            return False

    def geocode_location(self, location: Location) -> bool:
        """
        Geocode a location using its address or city and country.
        Updates the location with coordinates if successful.

        Args:
            location: The Location object to geocode

        Returns:
            True if geocoding was successful, False otherwise
        """
        try:
            # Determine what to geocode based on available information
            if location.address:
                geocode_query = location.address
                self._log(f"Geocoding using address: {geocode_query}")
            else:
                # Get country name from country code
                country = pycountry.countries.get(alpha_2=location.country.code)
                country_name = country.name if country else ""
                geocode_query = f"{location.city}, {country_name}"
                self._log(f"Geocoding using city and country: {geocode_query}")

            # Perform geocoding
            geocode_result = self.gmaps.geocode(geocode_query)

            if geocode_result:
                # Update location with geocoding results
                location.lat = geocode_result[0]["geometry"]["location"]["lat"]
                location.lng = geocode_result[0]["geometry"]["location"]["lng"]

                # If we didn't have an address before, update it from the geocode result
                if not location.address:
                    self.update_location_from_geocode_result(
                        location, geocode_result[0]
                    )

                self._log(f"Successfully geocoded: {location.lat}, {location.lng}")
                return True
            else:
                self._log(f"No geocoding results for: {geocode_query}", "warning")
                return False

        except Exception as e:
            self._log(f"Geocoding error: {str(e)}", "error")
            return False

    @staticmethod
    def deg2rad(deg):
        """Convert degrees to radians"""
        return deg / 360 * 2 * math.pi

    def get_distance_from_lat_lng_in_km(
        self, lat1: float, lng1: float, lat2: float, lng2: float
    ) -> float:
        """
        Calculate the distance between two points in kilometers using the Haversine formula.

        Args:
            lat1: Latitude of first point
            lng1: Longitude of first point
            lat2: Latitude of second point
            lng2: Longitude of second point

        Returns:
            Distance in kilometers
        """
        R = 6371  # Radius of the earth in km
        d_lat = self.deg2rad(lat2 - lat1)
        d_lng = self.deg2rad(lng2 - lng1)
        a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(
            self.deg2rad(lat1)
        ) * math.cos(self.deg2rad(lat2)) * math.sin(d_lng / 2) * math.sin(d_lng / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c  # Distance in km
        return d

    def get_nearby_locations(
        self, lat: float, lng: float, max_distance_km: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find locations near the specified coordinates.

        Args:
            lat: Latitude to search around
            lng: Longitude to search around
            max_distance_km: Maximum distance in kilometers (default: 0.5)

        Returns:
            List of dictionaries containing location objects and their distances
        """
        # Calculate bounding box for initial filtering (optimization)
        # 0.01 degrees is roughly 1km at the equator, adjust based on max_distance_km
        lat_range = max_distance_km * 0.01
        lng_range = max_distance_km * 0.01

        existing_locations = Location.objects.filter(
            lat__gte=lat - lat_range,
            lat__lte=lat + lat_range,
            lng__gte=lng - lng_range,
            lng__lte=lng + lng_range,
        )

        # Calculate exact distances and filter
        locations_with_distance = []
        for loc in existing_locations:
            dist = self.get_distance_from_lat_lng_in_km(lat, lng, loc.lat, loc.lng)
            if dist <= max_distance_km:
                locations_with_distance.append({"distance": dist, "location": loc})

        # Sort by distance
        return sorted(locations_with_distance, key=lambda x: x["distance"])

    def find_place_by_location(self, location: Location) -> Optional[Dict[str, Any]]:
        """
        Find a place using Google Places API based on a location.
        Useful for getting additional details like photos.

        Args:
            location: The Location object to find a place for

        Returns:
            Place details or None if no place was found
        """
        if not location.lat or not location.lng:
            self._log(f"Cannot find place without coordinates", "warning")
            return None

        try:
            # Try different search strategies
            place_id = None

            # Strategy 1: Find place from address
            if location.address:
                self._log(f"Searching for place using address: {location.address}")

                try:
                    find_place_result = self.gmaps.find_place(
                        input=location.address,
                        input_type="textquery",
                        fields=["place_id", "name", "formatted_address"],
                        location_bias=f"circle:5000@{location.lat},{location.lng}",
                    )

                    if find_place_result.get("candidates"):
                        place_id = find_place_result["candidates"][0]["place_id"]
                        self._log(
                            f"Found place from address: {find_place_result['candidates'][0].get('name', 'Unknown')}"
                        )
                except Exception as e:
                    self._log(f"Error in find_place: {str(e)}", "warning")

            # Strategy 2: Text search by address if find_place didn't work
            if not place_id and location.address:
                self._log(f"Trying text search with address")

                text_search_result = self.gmaps.places(
                    query=location.address,
                    location=(location.lat, location.lng),
                    radius=5000,  # 5km radius
                )

                if text_search_result.get("results"):
                    place_id = text_search_result["results"][0]["place_id"]
                    self._log(
                        f"Found place via text search: {text_search_result['results'][0].get('name', 'Unknown')}"
                    )

            # Strategy 3: Nearby search based on water type
            if not place_id:
                self._log(f"Trying nearby search for relevant places")

                # Determine place types based on water type
                place_types = ["natural_feature", "point_of_interest"]
                if location.water_type:
                    if location.water_type == "sea":
                        place_types = ["natural_feature", "beach"]
                    elif location.water_type == "lake":
                        place_types = ["natural_feature", "lake"]
                    elif location.water_type == "river":
                        place_types = ["natural_feature", "river"]
                    elif location.water_type == "pool":
                        place_types = ["swimming_pool"]

                # Try each place type
                for place_type in place_types:
                    nearby_search_result = self.gmaps.places_nearby(
                        location=(location.lat, location.lng),
                        radius=2000,  # 2km radius
                        type=place_type,
                    )

                    if nearby_search_result.get("results"):
                        place_id = nearby_search_result["results"][0]["place_id"]
                        self._log(
                            f"Found place via nearby search: {nearby_search_result['results'][0].get('name', 'Unknown')}"
                        )
                        break

            # If we found a place, get its details
            if place_id:
                place_details = self.gmaps.place(
                    place_id=place_id,
                    fields=["name", "photo", "formatted_address", "type", "geometry"],
                )
                return place_details["result"]
            else:
                self._log(f"No suitable place found for this location", "warning")
                return None

        except Exception as e:
            self._log(f"Error finding place: {str(e)}", "error")
            return None
