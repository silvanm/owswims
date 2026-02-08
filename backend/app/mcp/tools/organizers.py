"""
MCP Tools for Organizer CRUD operations.
"""
from datetime import datetime
from typing import List, Optional

from asgiref.sync import sync_to_async
from fastmcp import Context

from app.mcp.server import mcp


@mcp.tool
async def list_organizers(
    ctx: Context,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    has_upcoming_events: Optional[bool] = None,
) -> List[dict]:
    """
    List organizers with optional filtering.

    Args:
        limit: Maximum number of organizers to return (default 50, max 100)
        offset: Number of organizers to skip for pagination
        search: Search in organizer name
        has_upcoming_events: Filter to organizers with upcoming events

    Returns:
        List of organizer objects
    """
    from app.models import Organizer

    @sync_to_async
    def fetch_organizers():
        qs = Organizer.objects.all()

        if search:
            qs = qs.filter(name__icontains=search)

        if has_upcoming_events:
            # Filter to organizers with future events
            qs = qs.filter(events__date_start__gte=datetime.now()).distinct()

        limit_capped = min(limit, 100)
        qs = qs.order_by('name')[offset:offset + limit_capped]

        return [
            {
                "id": org.id,
                "name": org.name,
                "website": org.website,
                "slug": org.slug,
                "contact_email": org.contact_email,
                "language": org.language,
                "contact_status": org.contact_status,
            }
            for org in qs
        ]

    return await fetch_organizers()


@mcp.tool
async def get_organizer(ctx: Context, organizer_id: int) -> dict:
    """
    Get a single organizer by ID with full details.

    Args:
        organizer_id: The organizer ID to retrieve

    Returns:
        Organizer object with all fields and event count
    """
    from app.models import Organizer

    @sync_to_async
    def fetch_organizer():
        try:
            org = Organizer.objects.get(pk=organizer_id)
            total_events = org.events.count()
            upcoming_events = org.events.filter(
                date_start__gte=datetime.now()
            ).count()

            return {
                "id": org.id,
                "name": org.name,
                "website": org.website,
                "slug": org.slug,
                "contact_email": org.contact_email,
                "contact_form_url": org.contact_form_url,
                "contact_status": org.contact_status,
                "contact_notes": org.contact_notes,
                "language": org.language,
                "internal_comment": org.internal_comment,
                "last_contact_attempt": str(org.last_contact_attempt)
                if org.last_contact_attempt else None,
                "has_user_account": org.user is not None,
                "total_events": total_events,
                "upcoming_events": upcoming_events,
            }
        except Organizer.DoesNotExist:
            return None

    result = await fetch_organizer()

    if result is None:
        raise ValueError(f"Organizer with ID {organizer_id} not found")

    return result


@mcp.tool
async def create_organizer(
    ctx: Context,
    name: str,
    website: str,
    contact_email: Optional[str] = None,
    contact_form_url: Optional[str] = None,
    language: Optional[str] = None,
    internal_comment: Optional[str] = None,
) -> dict:
    """
    Create a new organizer.

    Args:
        name: Organizer name (required)
        website: Organizer website URL (required)
        contact_email: Contact email address
        contact_form_url: URL of contact form
        language: ISO language code (e.g., 'en', 'de', 'fr')
        internal_comment: Internal notes (not shown publicly)

    Returns:
        The created organizer object with assigned ID and auto-generated slug
    """
    from app.models import Organizer

    @sync_to_async
    def do_create():
        org = Organizer(
            name=name,
            website=website,
            contact_email=contact_email,
            contact_form_url=contact_form_url,
            language=language,
            internal_comment=internal_comment or "",
        )
        org.save()  # This auto-generates the slug

        return {
            "id": org.id,
            "name": org.name,
            "website": org.website,
            "slug": org.slug,
            "created": True,
        }

    return await do_create()


@mcp.tool
async def update_organizer(
    ctx: Context,
    organizer_id: int,
    name: Optional[str] = None,
    website: Optional[str] = None,
    contact_email: Optional[str] = None,
    contact_form_url: Optional[str] = None,
    language: Optional[str] = None,
    internal_comment: Optional[str] = None,
    contact_status: Optional[str] = None,
    contact_notes: Optional[str] = None,
) -> dict:
    """
    Update an existing organizer. Only provided fields are updated.

    Args:
        organizer_id: The organizer ID to update (required)
        name: Organizer name
        website: Organizer website URL
        contact_email: Contact email (use empty string to clear)
        contact_form_url: Contact form URL (use empty string to clear)
        language: ISO language code
        internal_comment: Internal notes
        contact_status: Status: pending, contacted, responded, completed,
            failed, needs_review
        contact_notes: Notes about contact attempts

    Returns:
        The updated organizer summary
    """
    from app.models import Organizer

    @sync_to_async
    def do_update():
        try:
            org = Organizer.objects.get(pk=organizer_id)
        except Organizer.DoesNotExist:
            raise ValueError(f"Organizer {organizer_id} not found")

        # Validate contact_status if provided
        valid_statuses = [
            'pending', 'contacted', 'responded',
            'completed', 'failed', 'needs_review'
        ]
        if contact_status is not None and contact_status not in valid_statuses:
            raise ValueError(
                f"Invalid contact_status '{contact_status}'. "
                f"Must be one of: {', '.join(valid_statuses)}"
            )

        if name is not None:
            org.name = name
        if website is not None:
            org.website = website
        if contact_email is not None:
            org.contact_email = contact_email if contact_email else None
        if contact_form_url is not None:
            org.contact_form_url = contact_form_url if contact_form_url else None
        if language is not None:
            org.language = language if language else None
        if internal_comment is not None:
            org.internal_comment = internal_comment
        if contact_status is not None:
            org.contact_status = contact_status
        if contact_notes is not None:
            org.contact_notes = contact_notes

        org.save()
        return {
            "id": org.id,
            "name": org.name,
            "slug": org.slug,
            "updated": True,
        }

    return await do_update()


@mcp.tool
async def delete_organizer(ctx: Context, organizer_id: int) -> dict:
    """
    Delete an organizer. Events referencing this organizer will have their
    organizer set to NULL.

    Args:
        organizer_id: The organizer ID to delete

    Returns:
        Confirmation of deletion with affected event count
    """
    from app.models import Organizer

    @sync_to_async
    def do_delete():
        try:
            org = Organizer.objects.get(pk=organizer_id)
            name = org.name
            event_count = org.events.count()

            # Events will have organizer set to NULL due to SET_NULL
            org.delete()

            return {
                "deleted": True,
                "id": organizer_id,
                "name": name,
                "events_affected": event_count,
                "note": f"{event_count} events now have no organizer"
                if event_count > 0 else None,
            }
        except Organizer.DoesNotExist:
            raise ValueError(f"Organizer {organizer_id} not found")

    return await do_delete()


@mcp.tool
async def search_organizers(
    ctx: Context,
    query: str,
    limit: int = 20,
) -> List[dict]:
    """
    Search organizers by name.

    Args:
        query: Search query (required)
        limit: Maximum results (default 20, max 50)

    Returns:
        List of matching organizers
    """
    from app.models import Organizer

    @sync_to_async
    def do_search():
        qs = Organizer.objects.filter(name__icontains=query)

        limit_capped = min(limit, 50)
        qs = qs.order_by('name')[:limit_capped]

        return [
            {
                "id": org.id,
                "name": org.name,
                "website": org.website,
                "slug": org.slug,
            }
            for org in qs
        ]

    return await do_search()


@mcp.tool
async def get_organizer_events(
    ctx: Context,
    organizer_id: int,
    include_past: bool = False,
    limit: int = 50,
) -> List[dict]:
    """
    Get all events for a specific organizer.

    Args:
        organizer_id: The organizer ID
        include_past: Include past events (default False, only upcoming)
        limit: Maximum events to return (default 50, max 100)

    Returns:
        List of events for this organizer
    """
    from app.models import Organizer, Event

    @sync_to_async
    def fetch_events():
        try:
            org = Organizer.objects.get(pk=organizer_id)
        except Organizer.DoesNotExist:
            raise ValueError(f"Organizer {organizer_id} not found")

        qs = Event.objects.filter(organizer=org).select_related('location')

        if not include_past:
            qs = qs.filter(date_start__gte=datetime.now())

        limit_capped = min(limit, 100)
        qs = qs.order_by('date_start')[:limit_capped]

        return [
            {
                "id": e.id,
                "name": e.name,
                "date_start": str(e.date_start),
                "date_end": str(e.date_end),
                "location": {
                    "city": e.location.city,
                    "country": str(e.location.country),
                } if e.location else None,
                "cancelled": e.cancelled or False,
            }
            for e in qs
        ]

    return await fetch_events()
