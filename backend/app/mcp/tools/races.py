"""
MCP Tools for Race CRUD operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from asgiref.sync import sync_to_async
from djmoney.money import Money
from fastmcp import Context

from app.mcp.server import mcp


@mcp.tool
async def list_races(
    ctx: Context,
    event_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    distance_min: Optional[float] = None,
    distance_max: Optional[float] = None,
    search: Optional[str] = None,
) -> List[dict]:
    """
    List races with optional filtering.

    Args:
        event_id: Filter by event ID
        limit: Maximum number of races to return (default 50, max 100)
        offset: Number of races to skip for pagination
        date_from: Filter races on or after this date (YYYY-MM-DD)
        date_to: Filter races on or before this date (YYYY-MM-DD)
        distance_min: Minimum distance in km
        distance_max: Maximum distance in km
        search: Fuzzy search in race name and event name (e.g. "zurich" finds "Zürich")

    Returns:
        List of race objects with event info
    """
    from app.models import Race
    from django.db.models import Q

    from app.mcp.utils import fuzzy_rank

    @sync_to_async
    def fetch_races():
        qs = Race.objects.select_related('event', 'event__location').all()

        if event_id:
            qs = qs.filter(event_id=event_id)

        if date_from:
            qs = qs.filter(
                date__gte=datetime.strptime(date_from, '%Y-%m-%d').date()
            )

        if date_to:
            qs = qs.filter(
                date__lte=datetime.strptime(date_to, '%Y-%m-%d').date()
            )

        if distance_min is not None:
            qs = qs.filter(distance__gte=distance_min)

        if distance_max is not None:
            qs = qs.filter(distance__lte=distance_max)

        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(event__name__icontains=search)
            )

        limit_capped = min(limit, 100)

        def _serialize(r):
            return {
                "id": r.id,
                "event_id": r.event_id,
                "event_name": r.event.name,
                "date": str(r.date),
                "race_time": str(r.race_time) if r.race_time else None,
                "distance": r.distance,
                "name": r.name,
                "wetsuit": r.wetsuit,
                "price": str(r.price) if r.price else None,
                "location": {
                    "city": r.event.location.city if r.event.location else None,
                    "country": str(r.event.location.country)
                    if r.event.location else None,
                },
            }

        if search:
            candidates = list(qs[:500])
            ranked = fuzzy_rank(
                candidates,
                lambda r: f"{r.name or ''} {r.event.name}",
                search,
            )
            return [_serialize(r) for r in ranked[offset:offset + limit_capped]]
        else:
            qs = qs.order_by('date', 'race_time')[offset:offset + limit_capped]
            return [_serialize(r) for r in qs]

    return await fetch_races()


@mcp.tool
async def search_races(
    ctx: Context,
    query: str,
    limit: int = 20,
) -> List[dict]:
    """
    Search races by name or event name with fuzzy matching.

    Args:
        query: Search query (required)
        limit: Maximum results (default 20, max 50)

    Returns:
        List of matching races sorted by relevance
    """
    from app.models import Race
    from django.db.models import Q

    from app.mcp.utils import fuzzy_rank

    @sync_to_async
    def do_search():
        qs = Race.objects.select_related('event', 'event__location').filter(
            Q(name__icontains=query) | Q(event__name__icontains=query)
        )

        candidates = list(qs[:500])
        limit_capped = min(limit, 50)
        ranked = fuzzy_rank(
            candidates,
            lambda r: f"{r.name or ''} {r.event.name}",
            query,
        )
        return [
            {
                "id": r.id,
                "event_id": r.event_id,
                "event_name": r.event.name,
                "date": str(r.date),
                "distance": r.distance,
                "name": r.name,
                "location": {
                    "city": r.event.location.city if r.event.location else None,
                    "country": str(r.event.location.country)
                    if r.event.location else None,
                },
            }
            for r in ranked[:limit_capped]
        ]

    return await do_search()


@mcp.tool
async def get_race(ctx: Context, race_id: int) -> dict:
    """
    Get a single race by ID with full details.

    Args:
        race_id: The race ID to retrieve

    Returns:
        Race object with all fields including event info
    """
    from app.models import Race

    @sync_to_async
    def fetch_race():
        try:
            r = Race.objects.select_related(
                'event', 'event__location', 'event__organizer'
            ).get(pk=race_id)

            return {
                "id": r.id,
                "event_id": r.event_id,
                "event_name": r.event.name,
                "date": str(r.date),
                "race_time": str(r.race_time) if r.race_time else None,
                "distance": r.distance,
                "name": r.name,
                "wetsuit": r.wetsuit,
                "price": str(r.price) if r.price else None,
                "coordinates": r.coordinates,
                "event": {
                    "id": r.event.id,
                    "name": r.event.name,
                    "website": r.event.website,
                    "location": {
                        "city": r.event.location.city,
                        "country": str(r.event.location.country),
                    } if r.event.location else None,
                    "organizer": {
                        "name": r.event.organizer.name,
                    } if r.event.organizer else None,
                },
            }
        except Race.DoesNotExist:
            return None

    result = await fetch_race()

    if result is None:
        raise ValueError(f"Race with ID {race_id} not found")

    return result


@mcp.tool
async def create_race(
    ctx: Context,
    event_id: int,
    date: str,
    distance: float,
    race_time: Optional[str] = None,
    name: Optional[str] = None,
    wetsuit: Optional[str] = None,
    price: Optional[float] = None,
) -> dict:
    """
    Create a new race for an event.

    Args:
        event_id: Parent event ID (required)
        date: Race date in YYYY-MM-DD format (required)
        distance: Distance in km (required)
        race_time: Start time in HH:MM format
        name: Race name/category (e.g., "Sprint", "Elite")
        wetsuit: Wetsuit policy: compulsory, optional, prohibited
        price: Entry price in EUR

    Returns:
        The created race object with assigned ID
    """
    from app.models import Race, Event

    @sync_to_async
    def do_create():
        # Verify event exists
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            raise ValueError(f"Event {event_id} not found")

        r = Race(
            event=event,
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            distance=distance,
            name=name,
            wetsuit=wetsuit,
        )

        if race_time:
            r.race_time = datetime.strptime(race_time, '%H:%M').time()

        if price is not None:
            r.price = Money(Decimal(str(price)), 'EUR')

        r.save()
        return {
            "id": r.id,
            "event_id": r.event_id,
            "date": str(r.date),
            "distance": r.distance,
            "created": True,
        }

    return await do_create()


@mcp.tool
async def update_race(
    ctx: Context,
    race_id: int,
    date: Optional[str] = None,
    distance: Optional[float] = None,
    race_time: Optional[str] = None,
    name: Optional[str] = None,
    wetsuit: Optional[str] = None,
    price: Optional[float] = None,
) -> dict:
    """
    Update an existing race. Only provided fields are updated.

    Args:
        race_id: The race ID to update (required)
        date: Race date in YYYY-MM-DD format
        distance: Distance in km
        race_time: Start time in HH:MM format (use empty string to clear)
        name: Race name/category
        wetsuit: Wetsuit policy: compulsory, optional, prohibited
        price: Entry price in EUR

    Returns:
        The updated race summary
    """
    from app.models import Race

    @sync_to_async
    def do_update():
        try:
            r = Race.objects.get(pk=race_id)
        except Race.DoesNotExist:
            raise ValueError(f"Race {race_id} not found")

        if date is not None:
            r.date = datetime.strptime(date, '%Y-%m-%d').date()
        if distance is not None:
            r.distance = distance
        if race_time is not None:
            if race_time == "":
                r.race_time = None
            else:
                r.race_time = datetime.strptime(race_time, '%H:%M').time()
        if name is not None:
            r.name = name if name else None
        if wetsuit is not None:
            r.wetsuit = wetsuit if wetsuit else None
        if price is not None:
            r.price = Money(Decimal(str(price)), 'EUR')

        r.save()
        return {
            "id": r.id,
            "event_id": r.event_id,
            "date": str(r.date),
            "distance": r.distance,
            "updated": True,
        }

    return await do_update()


@mcp.tool
async def delete_race(ctx: Context, race_id: int) -> dict:
    """
    Delete a race.

    Args:
        race_id: The race ID to delete

    Returns:
        Confirmation of deletion
    """
    from app.models import Race

    @sync_to_async
    def do_delete():
        try:
            r = Race.objects.select_related('event').get(pk=race_id)
            event_id = r.event_id
            event_name = r.event.name
            distance = r.distance
            r.delete()
            return {
                "deleted": True,
                "id": race_id,
                "event_id": event_id,
                "event_name": event_name,
                "distance": distance,
            }
        except Race.DoesNotExist:
            raise ValueError(f"Race {race_id} not found")

    return await do_delete()
