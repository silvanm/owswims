from django import forms
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils import timezone
from django.utils.translation import ugettext_lazy

from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from . import models
from .models import Race

admin.site.site_header = ugettext_lazy('Open-Water-Swims Admin')

admin.site.register(models.Organizer)

@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }


class RaceInline(admin.TabularInline):
    model = Race


class IsVerifiedFilter(admin.SimpleListFilter):
    title = 'is Verified'

    parameter_name = 'is_verified'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(verified_at__isnull=False)
        elif self.value() == 'no':
            return queryset.filter(verified_at__isnull=True)


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("date_start", "name", "locationstr", "water_type", "source")
    list_display_links = ("name",)
    list_filter = ("water_type", "source", IsVerifiedFilter, "organizer", "entry_quality")
    readonly_fields = ["edited_by", "edited_at"]
    inlines = [
        RaceInline,
    ]

    def get_queryset(self, request):
        # Only return events in the future
        return (
            super(EventAdmin, self)
                .get_queryset(request)
                .filter(date_start__gte=timezone.now())
        )

    def locationstr(self, obj):
        if obj.location:
            return f"{obj.location.city}, {obj.location.country}"
