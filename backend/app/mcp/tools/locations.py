"""
MCP Tools for Location CRUD operations.
"""
from typing import List, Optional

from asgiref.sync import sync_to_async
from fastmcp import Context

from app.mcp.server import mcp


@mcp.tool
async def list_locations(
    ctx: Context,
    limit: int = 50,
    offset: int = 0,
    country: Optional[str] = None,
    city: Optional[str] = None,
    water_type: Optional[str] = None,
    search: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_km: Optional[float] = None,
) -> List[dict]:
    """
    List locations with optional filtering.

    Args:
        limit: Maximum number of locations to return (default 50, max 100)
        offset: Number of locations to skip for pagination
        country: Filter by country code (e.g., 'CH', 'DE')
        city: Filter by city name (partial match)
        water_type: Filter by water type (river, sea, lake, pool)
        search: Fuzzy search in city and water_name fields (e.g. "zurich see" finds "Zürichsee")
        lat: Latitude for coordinate search (requires lng and radius_km)
        lng: Longitude for coordinate search (requires lat and radius_km)
        radius_km: Search radius in kilometers (requires lat and lng)

    Returns:
        List of location objects, sorted by distance when coordinate search is used
    """
    from app.models import Location
    from django.db.models import Q

    from app.mcp.utils import fuzzy_rank, haversine_km

    @sync_to_async
    def fetch_locations():
        qs = Location.objects.all()

        if country:
            qs = qs.filter(country=country.upper())

        if city:
            qs = qs.filter(city__icontains=city)

        if water_type:
            qs = qs.filter(water_type=water_type)

        if search:
            qs = qs.filter(
                Q(city__icontains=search) | Q(water_name__icontains=search)
            )

        # Coordinate bounding-box pre-filter
        geo_search = (lat is not None and lng is not None
                      and radius_km is not None)
        if geo_search:
            qs = qs.filter(lat__isnull=False, lng__isnull=False)
            # Rough bounding box to narrow candidates (~1 degree ≈ 111 km)
            delta = radius_km / 111.0
            qs = qs.filter(
                lat__gte=lat - delta, lat__lte=lat + delta,
                lng__gte=lng - delta, lng__lte=lng + delta,
            )

        limit_capped = min(limit, 100)

        def _serialize(loc, distance=None):
            result = {
                "id": loc.id,
                "city": loc.city,
                "country": str(loc.country),
                "water_name": loc.water_name,
                "water_type": loc.water_type,
                "lat": loc.lat,
                "lng": loc.lng,
                "address": loc.address,
                "average_rating": loc.average_rating,
            }
            if distance is not None:
                result["distance_km"] = round(distance, 1)
            return result

        if geo_search:
            # Precise haversine filter + sort by distance
            candidates = list(qs[:2000])
            with_dist = []
            for loc in candidates:
                d = haversine_km(lat, lng, loc.lat, loc.lng)
                if d <= radius_km:
                    with_dist.append((d, loc))
            with_dist.sort(key=lambda x: x[0])
            return [
                _serialize(loc, distance=d)
                for d, loc in with_dist[offset:offset + limit_capped]
            ]
        elif search:
            candidates = list(qs[:500])
            ranked = fuzzy_rank(
                candidates,
                lambda loc: f"{loc.city} {loc.water_name or ''}",
                search,
            )
            return [_serialize(loc) for loc in ranked[offset:offset + limit_capped]]
        else:
            qs = qs.order_by('city')[offset:offset + limit_capped]
            return [_serialize(loc) for loc in qs]

    return await fetch_locations()


@mcp.tool
async def get_location(ctx: Context, location_id: int) -> dict:
    """
    Get a single location by ID with full details.

    Args:
        location_id: The location ID to retrieve

    Returns:
        Location object with all fields and event count
    """
    from app.models import Location

    @sync_to_async
    def fetch_location():
        try:
            loc = Location.objects.get(pk=location_id)
            event_count = loc.events.count()

            return {
                "id": loc.id,
                "city": loc.city,
                "country": str(loc.country),
                "water_name": loc.water_name,
                "water_type": loc.water_type,
                "lat": loc.lat,
                "lng": loc.lng,
                "address": loc.address,
                "average_rating": loc.average_rating,
                "verified_at": str(loc.verified_at) if loc.verified_at else None,
                "event_count": event_count,
            }
        except Location.DoesNotExist:
            return None

    result = await fetch_location()

    if result is None:
        raise ValueError(f"Location with ID {location_id} not found")

    return result


@mcp.tool
async def create_location(
    ctx: Context,
    city: str,
    country: str,
    water_name: Optional[str] = None,
    water_type: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    address: Optional[str] = None,
) -> dict:
    """
    Create a new location.

    Args:
        city: City name (required)
        country: Country code, 2-letter ISO (required, e.g., 'CH', 'DE')
        water_name: Name of water body (e.g., "Lake Zurich")
        water_type: Type of water: river, sea, lake, pool
        lat: Latitude coordinate
        lng: Longitude coordinate
        address: Street address

    Returns:
        The created location object with assigned ID
    """
    from app.models import Location

    @sync_to_async
    def do_create():
        # Validate water_type
        valid_water_types = ['river', 'sea', 'lake', 'pool']
        if water_type and water_type not in valid_water_types:
            raise ValueError(
                f"Invalid water_type '{water_type}'. "
                f"Must be one of: {', '.join(valid_water_types)}"
            )

        loc = Location(
            city=city,
            country=country.upper(),
            water_name=water_name,
            water_type=water_type,
            lat=lat,
            lng=lng,
            address=address,
        )
        loc.save()

        return {
            "id": loc.id,
            "city": loc.city,
            "country": str(loc.country),
            "water_name": loc.water_name,
            "created": True,
        }

    return await do_create()


@mcp.tool
async def update_location(
    ctx: Context,
    location_id: int,
    city: Optional[str] = None,
    country: Optional[str] = None,
    water_name: Optional[str] = None,
    water_type: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    address: Optional[str] = None,
) -> dict:
    """
    Update an existing location. Only provided fields are updated.

    Args:
        location_id: The location ID to update (required)
        city: City name
        country: Country code, 2-letter ISO
        water_name: Name of water body (use empty string to clear)
        water_type: Type of water: river, sea, lake, pool (use empty string to clear)
        lat: Latitude coordinate
        lng: Longitude coordinate
        address: Street address (use empty string to clear)

    Returns:
        The updated location summary
    """
    from app.models import Location

    @sync_to_async
    def do_update():
        try:
            loc = Location.objects.get(pk=location_id)
        except Location.DoesNotExist:
            raise ValueError(f"Location {location_id} not found")

        # Validate water_type if provided
        valid_water_types = ['river', 'sea', 'lake', 'pool', '']
        if water_type is not None and water_type not in valid_water_types:
            raise ValueError(
                f"Invalid water_type '{water_type}'. "
                f"Must be one of: river, sea, lake, pool"
            )

        if city is not None:
            loc.city = city
        if country is not None:
            loc.country = country.upper()
        if water_name is not None:
            loc.water_name = water_name if water_name else None
        if water_type is not None:
            loc.water_type = water_type if water_type else None
        if lat is not None:
            loc.lat = lat
        if lng is not None:
            loc.lng = lng
        if address is not None:
            loc.address = address if address else None

        loc.save()
        return {
            "id": loc.id,
            "city": loc.city,
            "country": str(loc.country),
            "updated": True,
        }

    return await do_update()


@mcp.tool
async def delete_location(ctx: Context, location_id: int) -> dict:
    """
    Delete a location. Will fail if any events reference this location.

    Args:
        location_id: The location ID to delete

    Returns:
        Confirmation of deletion
    """
    from app.models import Location

    @sync_to_async
    def do_delete():
        try:
            loc = Location.objects.get(pk=location_id)
            event_count = loc.events.count()

            if event_count > 0:
                raise ValueError(
                    f"Cannot delete location {location_id}: "
                    f"it has {event_count} events. "
                    f"Delete or reassign events first."
                )

            city = loc.city
            country = str(loc.country)
            loc.delete()

            return {
                "deleted": True,
                "id": location_id,
                "city": city,
                "country": country,
            }
        except Location.DoesNotExist:
            raise ValueError(f"Location {location_id} not found")

    return await do_delete()


@mcp.tool
async def search_locations(
    ctx: Context,
    query: str,
    country: Optional[str] = None,
    limit: int = 20,
) -> List[dict]:
    """
    Search locations by name. Searches in city and water_name fields.

    Args:
        query: Search query (required)
        country: Filter by country code
        limit: Maximum results (default 20, max 50)

    Returns:
        List of matching locations
    """
    from app.models import Location
    from django.db.models import Q

    @sync_to_async
    def do_search():
        from app.mcp.utils import fuzzy_rank

        qs = Location.objects.filter(
            Q(city__icontains=query) | Q(water_name__icontains=query)
        )

        if country:
            qs = qs.filter(country=country.upper())

        candidates = list(qs[:500])
        limit_capped = min(limit, 50)
        ranked = fuzzy_rank(
            candidates,
            lambda loc: f"{loc.city} {loc.water_name or ''}",
            query,
        )
        return [
            {
                "id": loc.id,
                "city": loc.city,
                "country": str(loc.country),
                "water_name": loc.water_name,
                "water_type": loc.water_type,
                "display": str(loc),
            }
            for loc in ranked[:limit_capped]
        ]

    return await do_search()


@mcp.tool
async def search_locations_by_coordinates(
    ctx: Context,
    lat: float,
    lng: float,
    radius_km: float = 50.0,
    water_type: Optional[str] = None,
    limit: int = 20,
) -> List[dict]:
    """
    Search locations near a geographic point. Returns locations within
    the given radius, sorted by distance (closest first).

    Args:
        lat: Latitude of the center point (required)
        lng: Longitude of the center point (required)
        radius_km: Search radius in kilometers (default 50)
        water_type: Filter by water type (river, sea, lake, pool)
        limit: Maximum results (default 20, max 50)

    Returns:
        List of matching locations with distance_km field
    """
    from app.models import Location

    from app.mcp.utils import haversine_km

    @sync_to_async
    def do_search():
        qs = Location.objects.filter(lat__isnull=False, lng__isnull=False)

        if water_type:
            qs = qs.filter(water_type=water_type)

        # Bounding box pre-filter (~1 degree ≈ 111 km)
        delta = radius_km / 111.0
        qs = qs.filter(
            lat__gte=lat - delta, lat__lte=lat + delta,
            lng__gte=lng - delta, lng__lte=lng + delta,
        )

        candidates = list(qs[:2000])
        limit_capped = min(limit, 50)

        with_dist = []
        for loc in candidates:
            d = haversine_km(lat, lng, loc.lat, loc.lng)
            if d <= radius_km:
                with_dist.append((d, loc))
        with_dist.sort(key=lambda x: x[0])

        return [
            {
                "id": loc.id,
                "city": loc.city,
                "country": str(loc.country),
                "water_name": loc.water_name,
                "water_type": loc.water_type,
                "lat": loc.lat,
                "lng": loc.lng,
                "distance_km": round(d, 1),
                "display": str(loc),
            }
            for d, loc in with_dist[:limit_capped]
        ]

    return await do_search()
