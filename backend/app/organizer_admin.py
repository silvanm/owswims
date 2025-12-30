"""
Separate Django admin site for organizers to manage their events and profile.

This admin site is accessible at /organizer-admin/ and is restricted to users
who have a linked Organizer record.
"""

from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from app.models import Organizer, Event, Location, Race


class OrganizerLocationForm(forms.ModelForm):
    """Simple location form for organizers without Google Maps widget."""

    # Override the address field to use a simple text widget
    address = forms.CharField(
        max_length=200,
        required=False,
        help_text=_(
            "Optional: Full address for precise map placement. "
            "If left empty, we'll use the city and country to determine coordinates."
        ),
        widget=forms.TextInput(attrs={"size": 60}),
    )

    class Meta:
        model = Location
        fields = ["city", "water_name", "water_type", "country", "address", "header_photo"]
        help_texts = {
            "city": _("The city or town where the event takes place"),
            "water_name": _("Name of the body of water (e.g., 'Lake Zurich', 'Rhine River')"),
            "water_type": _("Type of water body - helps swimmers know what to expect"),
            "country": _("Country where the location is"),
            "header_photo": _("A scenic photo of the location (shown on the event page)"),
        }


class OrganizerAdminSite(admin.AdminSite):
    """Custom admin site for organizers."""

    site_header = _("Open Water Swims - Organizer Portal (Beta)")
    site_title = _("Organizer Portal (Beta)")
    index_title = _("Manage Your Events")
    login_template = "organizer_admin/login.html"

    def has_permission(self, request):
        """Only allow users linked to an organizer."""
        return (
            request.user.is_active
            and hasattr(request.user, "organizer")
            and request.user.organizer is not None
        )


# Create the organizer admin site instance
organizer_admin_site = OrganizerAdminSite(name="organizer_admin")


class OrganizerProfileAdmin(admin.ModelAdmin):
    """Admin for organizers to edit their own profile."""

    fields = ["name", "website", "logo", "contact_email"]
    list_display = ["name", "website"]

    fieldsets = None  # Use fields instead of fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add help texts for profile fields
        if "name" in form.base_fields:
            form.base_fields["name"].help_text = _("Your organization's name as shown to swimmers")
        if "website" in form.base_fields:
            form.base_fields["website"].help_text = _("Your main website URL")
        if "logo" in form.base_fields:
            form.base_fields["logo"].help_text = _("Your organization's logo (displayed on event pages)")
        if "contact_email" in form.base_fields:
            form.base_fields["contact_email"].help_text = _("Email for swimmer inquiries (not shown publicly)")
        return form

    def get_queryset(self, request):
        """Only show the organizer's own profile."""
        qs = super().get_queryset(request)
        if hasattr(request.user, "organizer") and request.user.organizer:
            return qs.filter(pk=request.user.organizer.pk)
        return qs.none()

    def has_add_permission(self, request):
        """Organizers cannot create new organizer profiles."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Organizers cannot delete their profile."""
        return False

    def has_change_permission(self, request, obj=None):
        """Only allow changing their own organizer."""
        if obj is None:
            return True
        return (
            hasattr(request.user, "organizer")
            and request.user.organizer
            and obj.pk == request.user.organizer.pk
        )

    def has_view_permission(self, request, obj=None):
        """Allow viewing their own organizer."""
        return self.has_change_permission(request, obj)

    def has_module_permission(self, request):
        """Show in admin sidebar."""
        return hasattr(request.user, "organizer") and request.user.organizer is not None


class OrganizerRaceInline(admin.TabularInline):
    """Inline for organizers to manage races within an event.

    Each race represents a specific distance/category at your event.
    For example, a 5km race and a 10km race would be two separate entries.
    """

    model = Race
    extra = 1  # Show 1 empty form for adding new races
    fields = ["date", "race_time", "distance", "name", "wetsuit", "price"]
    verbose_name = _("Race / Distance")
    verbose_name_plural = _("Races / Distances (add one row per distance offered)")

    def has_add_permission(self, request, obj=None):
        """Allow adding races to events owned by the organizer."""
        return hasattr(request.user, "organizer") and request.user.organizer is not None

    def has_change_permission(self, request, obj=None):
        """Allow changing races on events owned by the organizer."""
        return hasattr(request.user, "organizer") and request.user.organizer is not None

    def has_delete_permission(self, request, obj=None):
        """Allow deleting races from events owned by the organizer."""
        return hasattr(request.user, "organizer") and request.user.organizer is not None

    def has_view_permission(self, request, obj=None):
        """Allow viewing races on events owned by the organizer."""
        return hasattr(request.user, "organizer") and request.user.organizer is not None


class OrganizerEventAdmin(admin.ModelAdmin):
    """Admin for organizers to edit their events."""

    # Use default template (not the custom one with crawl link)
    change_list_template = "admin/change_list.html"

    inlines = [OrganizerRaceInline]

    list_display = ["name", "date_start", "location", "active_user_count"]
    list_filter = ["date_start"]
    search_fields = ["name"]
    ordering = ["-date_start"]

    fieldsets = [
        (None, {
            "fields": ["name", "website", "description", "flyer_image"],
        }),
        (_("Dates & Location"), {
            "fields": ["date_start", "date_end", "location", "water_temp"],
            "description": _("Set the event dates and choose or create a location."),
        }),
        (_("Requirements"), {
            "fields": ["needs_medical_certificate", "needs_license", "with_ranking"],
            "description": _("Let swimmers know what they need to participate."),
        }),
        (_("Status"), {
            "fields": ["sold_out", "cancelled"],
            "description": _("Update if registration is closed or the event is cancelled."),
        }),
        (_("Statistics (read-only)"), {
            "fields": ["active_user_count", "verified_at"],
            "description": _("These fields are automatically updated by our system."),
            "classes": ["collapse"],
        }),
    ]
    readonly_fields = ["active_user_count", "verified_at"]
    autocomplete_fields = ["location"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add help texts for event fields
        help_texts = {
            "name": _("The official name of your event"),
            "website": _("Link to your event's registration or info page"),
            "description": _("A brief description shown to swimmers (supports basic formatting)"),
            "flyer_image": _("Upload your event flyer or poster (optional)"),
            "date_start": _("First day of the event"),
            "date_end": _("Last day of the event (same as start date for single-day events)"),
            "location": _("Select an existing location or create a new one"),
            "water_temp": _("Expected water temperature in Celsius (helps swimmers prepare)"),
            "needs_medical_certificate": _("Is a medical certificate required to participate?"),
            "needs_license": _("Is a federation license required?"),
            "with_ranking": _("Is this a timed race with results/rankings? (Uncheck for casual swims)"),
            "sold_out": _("Check if registration is full/closed"),
            "cancelled": _("Check if the event has been cancelled"),
            "active_user_count": _("Number of swimmers viewing this event (from analytics)"),
            "verified_at": _("When we last verified the event details"),
        }
        for field_name, help_text in help_texts.items():
            if field_name in form.base_fields:
                form.base_fields[field_name].help_text = help_text
        return form

    def get_queryset(self, request):
        """Only show events belonging to the organizer."""
        qs = super().get_queryset(request)
        if hasattr(request.user, "organizer") and request.user.organizer:
            return qs.filter(organizer=request.user.organizer)
        return qs.none()

    def has_add_permission(self, request):
        """Organizers can add new events."""
        return hasattr(request.user, "organizer") and request.user.organizer is not None

    def has_delete_permission(self, request, obj=None):
        """Organizers cannot delete events."""
        return False

    def get_fieldsets(self, request, obj=None):
        """Hide statistics section when adding a new event."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj is None:
            # When adding, exclude the Statistics section
            return [fs for fs in fieldsets if fs[0] != _("Statistics (read-only)")]
        return fieldsets

    def save_model(self, request, obj, form, change):
        """Set sensible defaults for hidden fields when creating events."""
        if not change:
            # Set organizer to the logged-in user's organizer
            if hasattr(request.user, "organizer") and request.user.organizer:
                obj.organizer = request.user.organizer
            # Set created_by to the logged-in user
            obj.created_by = request.user
            # Track source as organizer portal
            obj.source = "organizer_portal"
            # Mark as complete since manually created
            obj.entry_quality = "complete"
            # Ensure not invisible
            obj.invisible = False

        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        """Only allow changing events belonging to their organizer."""
        if obj is None:
            return True
        return (
            hasattr(request.user, "organizer")
            and request.user.organizer
            and obj.organizer == request.user.organizer
        )

    def has_view_permission(self, request, obj=None):
        """Allow viewing events belonging to their organizer."""
        return self.has_change_permission(request, obj)

    def has_module_permission(self, request):
        """Show in admin sidebar."""
        return hasattr(request.user, "organizer") and request.user.organizer is not None


class OrganizerLocationAdmin(admin.ModelAdmin):
    """Admin for organizers to create and edit locations for their events."""

    form = OrganizerLocationForm  # Simple form without Google Maps widget

    list_display = ["city", "water_name", "country", "is_verified"]
    fields = [
        "city",
        "water_name",
        "water_type",
        "country",
        "address",
        "header_photo",
    ]
    search_fields = ["city", "water_name"]

    def get_queryset(self, request):
        """Show locations used by their events or created by them."""
        from django.db.models import Q

        qs = super().get_queryset(request)
        if hasattr(request.user, "organizer") and request.user.organizer:
            organizer = request.user.organizer
            return qs.filter(
                Q(events__organizer=organizer) | Q(created_by_organizer=organizer)
            ).distinct()
        return qs.none()

    def has_add_permission(self, request):
        """Organizers can create new locations."""
        return True

    def has_delete_permission(self, request, obj=None):
        """Organizers cannot delete locations."""
        return False

    def has_change_permission(self, request, obj=None):
        """Allow changing locations linked to their events or created by them."""
        if obj is None:
            return True
        if hasattr(request.user, "organizer") and request.user.organizer:
            organizer = request.user.organizer
            # Allow if organizer created this location or has events using it
            return (
                obj.created_by_organizer == organizer
                or obj.events.filter(organizer=organizer).exists()
            )
        return False

    def has_view_permission(self, request, obj=None):
        """Allow viewing locations linked to their events or created by them."""
        return self.has_change_permission(request, obj)

    def has_module_permission(self, request):
        """Show in admin sidebar."""
        return hasattr(request.user, "organizer") and request.user.organizer is not None

    def save_model(self, request, obj, form, change):
        """Set created_by_organizer on create and auto-geocode on save."""
        from django.contrib import messages

        # Set created_by_organizer for new locations
        if not change and hasattr(request.user, "organizer") and request.user.organizer:
            obj.created_by_organizer = request.user.organizer

        super().save_model(request, obj, form, change)

        # Auto-geocode if no coordinates (uses address or city+country as fallback)
        if not obj.lat or not obj.lng:
            from app.services.geocoding_service import GeocodingService

            try:
                geocoding_service = GeocodingService()
                if geocoding_service.geocode_location(obj):
                    obj.save()  # Save the geocoded coordinates
                    messages.success(
                        request,
                        _("Location coordinates were automatically determined from the address.")
                    )
                else:
                    messages.warning(
                        request,
                        _("Could not determine coordinates automatically. "
                          "Please check the address or city/country fields.")
                    )
            except Exception as e:
                messages.warning(
                    request,
                    _("Geocoding failed: %(error)s. Coordinates were not set.") % {"error": str(e)}
                )


# Register models with the organizer admin site
organizer_admin_site.register(Organizer, OrganizerProfileAdmin)
organizer_admin_site.register(Event, OrganizerEventAdmin)
organizer_admin_site.register(Location, OrganizerLocationAdmin)
