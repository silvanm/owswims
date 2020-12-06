from django.contrib import admin
from django.utils import timezone

# Register your models here.
from . import models
from .models import Race

admin.site.register(models.Location)
admin.site.register(models.Organizer)


class RaceInline(admin.TabularInline):
    model = Race


class IsVerifiedFilter(admin.SimpleListFilter):
    title = 'is Verified'

    parameter_name = 'is_verified'

    def lookups(self, request, model_admin):
        return (
            (True, 'Yes'),
            (False, 'No'),
        )

    def queryset(self, request, queryset):
        return queryset.filter(verified_at__isnull=not self.value())


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("date_start", "name", "locationstr", "water_type", "source")
    list_display_links = ("name",)
    list_filter = ("water_type", "source", IsVerifiedFilter)
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
