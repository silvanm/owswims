"""
MCP Tools for Event CRUD operations.
"""
from datetime import datetime
from typing import List, Optional

from asgiref.sync import sync_to_async
from fastmcp import Context

from app.mcp.server import mcp


@mcp.tool
async def list_events(
    ctx: Context,
    limit: int = 50,
    offset: int = 0,
    country: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    organizer_id: Optional[int] = None,
    include_invisible: bool = False,
    include_cancelled: bool = True,
) -> List[dict]:
    """
    List events with optional filtering.

    Args:
        limit: Maximum number of events to return (default 50, max 100)
        offset: Number of events to skip for pagination
        country: Filter by country code (e.g., 'CH', 'DE')
        date_from: Filter events starting on or after this date (YYYY-MM-DD)
        date_to: Filter events starting on or before this date (YYYY-MM-DD)
        organizer_id: Filter by organizer ID
        include_invisible: Include hidden events (default False)
        include_cancelled: Include cancelled events (default True)

    Returns:
        List of event objects with id, name, dates, location, and organizer info
    """
    from app.models import Event

    @sync_to_async
    def fetch_events():
        qs = Event.objects.select_related('location', 'organizer').all()

        if not include_invisible:
            qs = qs.filter(invisible=False)

        if not include_cancelled:
            qs = qs.filter(cancelled=False)

        if country:
            qs = qs.filter(location__country=country.upper())

        if date_from:
            qs = qs.filter(
                date_start__gte=datetime.strptime(date_from, '%Y-%m-%d').date()
            )

        if date_to:
            qs = qs.filter(
                date_start__lte=datetime.strptime(date_to, '%Y-%m-%d').date()
            )

        if organizer_id:
            qs = qs.filter(organizer_id=organizer_id)

        limit_capped = min(limit, 100)
        qs = qs.order_by('date_start')[offset:offset + limit_capped]

        return [
            {
                "id": e.id,
                "name": e.name,
                "date_start": str(e.date_start),
                "date_end": str(e.date_end),
                "website": e.website or "",
                "description": (e.description or "")[:200],  # Truncate for list
                "cancelled": e.cancelled or False,
                "invisible": e.invisible or False,
                "location": {
                    "id": e.location.id,
                    "city": e.location.city,
                    "country": str(e.location.country),
                    "water_name": e.location.water_name,
                } if e.location else None,
                "organizer": {
                    "id": e.organizer.id,
                    "name": e.organizer.name,
                } if e.organizer else None,
            }
            for e in qs
        ]

    return await fetch_events()


@mcp.tool
async def get_event(ctx: Context, event_id: int) -> dict:
    """
    Get a single event by ID with full details including races.

    Args:
        event_id: The event ID to retrieve

    Returns:
        Event object with all fields including related races
    """
    from app.models import Event

    @sync_to_async
    def fetch_event():
        try:
            e = Event.objects.select_related(
                'location', 'organizer'
            ).prefetch_related('races').get(pk=event_id)

            return {
                "id": e.id,
                "name": e.name,
                "date_start": str(e.date_start),
                "date_end": str(e.date_end),
                "website": e.website or "",
                "description": e.description or "",
                "cancelled": e.cancelled or False,
                "invisible": e.invisible or False,
                "water_temp": e.water_temp,
                "needs_medical_certificate": e.needs_medical_certificate,
                "needs_license": e.needs_license,
                "sold_out": e.sold_out,
                "location": {
                    "id": e.location.id,
                    "city": e.location.city,
                    "country": str(e.location.country),
                    "water_name": e.location.water_name,
                    "water_type": e.location.water_type,
                    "lat": e.location.lat,
                    "lng": e.location.lng,
                } if e.location else None,
                "organizer": {
                    "id": e.organizer.id,
                    "name": e.organizer.name,
                    "website": e.organizer.website,
                    "slug": e.organizer.slug,
                } if e.organizer else None,
                "races": [
                    {
                        "id": r.id,
                        "date": str(r.date),
                        "race_time": str(r.race_time) if r.race_time else None,
                        "distance": r.distance,
                        "name": r.name,
                        "wetsuit": r.wetsuit,
                        "price": str(r.price) if r.price else None,
                    }
                    for r in e.races.all()
                ],
            }
        except Event.DoesNotExist:
            return None

    result = await fetch_event()

    if result is None:
        raise ValueError(f"Event with ID {event_id} not found")

    return result


@mcp.tool
async def create_event(
    ctx: Context,
    name: str,
    date_start: str,
    date_end: str,
    location_id: Optional[int] = None,
    organizer_id: Optional[int] = None,
    website: Optional[str] = None,
    description: Optional[str] = None,
    cancelled: bool = False,
    invisible: bool = False,
    water_temp: Optional[float] = None,
    needs_medical_certificate: Optional[bool] = None,
    needs_license: Optional[bool] = None,
) -> dict:
    """
    Create a new event.

    Args:
        name: Event name (required)
        date_start: Start date in YYYY-MM-DD format (required)
        date_end: End date in YYYY-MM-DD format (required)
        location_id: Location ID (optional)
        organizer_id: Organizer ID (optional)
        website: Event website URL
        description: Public description
        cancelled: Is event cancelled
        invisible: Hide from public
        water_temp: Water temperature in Celsius
        needs_medical_certificate: Medical certificate required
        needs_license: License required

    Returns:
        The created event object with assigned ID
    """
    from app.models import Event, Location, Organizer

    @sync_to_async
    def do_create():
        e = Event(
            name=name,
            date_start=datetime.strptime(date_start, '%Y-%m-%d').date(),
            date_end=datetime.strptime(date_end, '%Y-%m-%d').date(),
            website=website or "",
            description=description or "",
            cancelled=cancelled,
            invisible=invisible,
            water_temp=water_temp,
            needs_medical_certificate=needs_medical_certificate,
            needs_license=needs_license,
        )

        if location_id:
            try:
                e.location = Location.objects.get(pk=location_id)
            except Location.DoesNotExist:
                raise ValueError(f"Location {location_id} not found")

        if organizer_id:
            try:
                e.organizer = Organizer.objects.get(pk=organizer_id)
            except Organizer.DoesNotExist:
                raise ValueError(f"Organizer {organizer_id} not found")

        e.save()
        return {
            "id": e.id,
            "name": e.name,
            "date_start": str(e.date_start),
            "date_end": str(e.date_end),
            "created": True,
        }

    return await do_create()


@mcp.tool
async def update_event(
    ctx: Context,
    event_id: int,
    name: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    location_id: Optional[int] = None,
    organizer_id: Optional[int] = None,
    website: Optional[str] = None,
    description: Optional[str] = None,
    cancelled: Optional[bool] = None,
    invisible: Optional[bool] = None,
    water_temp: Optional[float] = None,
    needs_medical_certificate: Optional[bool] = None,
    needs_license: Optional[bool] = None,
    sold_out: Optional[bool] = None,
) -> dict:
    """
    Update an existing event. Only provided fields are updated.

    Args:
        event_id: The event ID to update (required)
        name: Event name
        date_start: Start date in YYYY-MM-DD format
        date_end: End date in YYYY-MM-DD format
        location_id: Location ID
        organizer_id: Organizer ID
        website: Event website URL
        description: Public description
        cancelled: Is event cancelled
        invisible: Hide from public
        water_temp: Water temperature in Celsius
        needs_medical_certificate: Medical certificate required
        needs_license: License required
        sold_out: Is event sold out

    Returns:
        The updated event summary
    """
    from app.models import Event, Location, Organizer

    @sync_to_async
    def do_update():
        try:
            e = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            raise ValueError(f"Event {event_id} not found")

        # Apply updates for provided fields
        if name is not None:
            e.name = name
        if date_start is not None:
            e.date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        if date_end is not None:
            e.date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        if website is not None:
            e.website = website
        if description is not None:
            e.description = description
        if cancelled is not None:
            e.cancelled = cancelled
        if invisible is not None:
            e.invisible = invisible
        if water_temp is not None:
            e.water_temp = water_temp
        if needs_medical_certificate is not None:
            e.needs_medical_certificate = needs_medical_certificate
        if needs_license is not None:
            e.needs_license = needs_license
        if sold_out is not None:
            e.sold_out = sold_out

        if location_id is not None:
            try:
                e.location = Location.objects.get(pk=location_id)
            except Location.DoesNotExist:
                raise ValueError(f"Location {location_id} not found")

        if organizer_id is not None:
            try:
                e.organizer = Organizer.objects.get(pk=organizer_id)
            except Organizer.DoesNotExist:
                raise ValueError(f"Organizer {organizer_id} not found")

        e.save()
        return {
            "id": e.id,
            "name": e.name,
            "date_start": str(e.date_start),
            "updated": True,
        }

    return await do_update()


@mcp.tool
async def delete_event(ctx: Context, event_id: int) -> dict:
    """
    Delete an event. WARNING: This also deletes all associated races!

    Args:
        event_id: The event ID to delete

    Returns:
        Confirmation of deletion
    """
    from app.models import Event

    @sync_to_async
    def do_delete():
        try:
            e = Event.objects.get(pk=event_id)
            name = e.name
            race_count = e.races.count()
            e.delete()
            return {
                "deleted": True,
                "id": event_id,
                "name": name,
                "races_deleted": race_count,
            }
        except Event.DoesNotExist:
            raise ValueError(f"Event {event_id} not found")

    return await do_delete()
