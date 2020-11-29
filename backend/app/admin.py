from django.contrib import admin
from django.utils import timezone

# Register your models here.
from . import models
from .models import Race

admin.site.register(models.Location)
admin.site.register(models.Organizer)


class RaceInline(admin.TabularInline):
    model = Race


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("date_start", "name", "locationstr", "water_type")
    list_display_links = ("name",)
    list_filter = ("water_type", "location__country")
    inlines = [
        RaceInline,
    ]

    def get_queryset(self, request):
        return (
            super(EventAdmin, self)
            .get_queryset(request)
            .filter(date_start__gte=timezone.now())
        )

    def locationstr(self, obj):
        return f"{obj.location.city}, {obj.location.country}"
