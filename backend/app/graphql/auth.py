"""
Object-level authorization for GraphQL mutations.

Staff can do anything. Organizer users can only modify their own organizer's
events, races, organizer record, and locations used by their events.
"""

from django.core.exceptions import PermissionDenied

from app.models import Event, Location, Organizer, Race


def _user_organizer_id(user):
    """Return the organizer pk for this user, or None."""
    if not user or not user.is_authenticated:
        return None
    try:
        org = Organizer.objects.get(user=user)
        return org.pk
    except Organizer.DoesNotExist:
        return None


def can_edit_event(user, event):
    """User may edit this event if staff or the event's organizer."""
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    if not event.organizer_id:
        return False
    return event.organizer.user_id == user.id


def can_edit_organizer(user, organizer):
    """User may edit this organizer if staff or the organizer's linked user."""
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return getattr(organizer, "user_id", None) == user.id


def can_edit_location(user, location):
    """User may edit this location if staff or an organizer with an event at this location."""
    if not user or not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    org_id = _user_organizer_id(user)
    if not org_id:
        return False
    return location.event_set.filter(organizer_id=org_id).exists()


def can_edit_race(user, race):
    """User may edit this race if they can edit the race's event."""
    return can_edit_event(user, race.event)


def require_can_edit_event(user, event):
    if not can_edit_event(user, event):
        raise PermissionDenied("You do not have permission to edit this event.")


def require_can_edit_organizer(user, organizer):
    if not can_edit_organizer(user, organizer):
        raise PermissionDenied("You do not have permission to edit this organizer.")


def require_can_edit_location(user, location):
    if not can_edit_location(user, location):
        raise PermissionDenied("You do not have permission to edit this location.")


def require_can_edit_race(user, race):
    if not can_edit_race(user, race):
        raise PermissionDenied("You do not have permission to edit this race.")
