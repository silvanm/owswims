from datetime import datetime
from urllib.parse import urlencode

import requests
from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.utils.translation import ugettext_lazy
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter
from model_clone import CloneModelAdmin
from django_q.tasks import async_task, result

from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from . import models
from .models import Race, Event, Location, Review

admin.site.site_header = ugettext_lazy("Open-Water-Swims Admin")


@admin.register(models.Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "website_link", "public_url", "number_of_events"]
    readonly_fields = ["public_url", "website_link", "number_of_events"]

    def public_url(self, obj):
        if obj.slug:
            url = settings.FRONTEND_URL + "?" + urlencode({"organizer": obj.slug})
            return format_html(f'<a target="_blank" href="{url}">{obj.slug}</a>')
        else:
            return ""

    def website_link(self, obj):
        if obj.website:
            return format_html(
                f'<a target="_blank" href="{obj.website}">{obj.website}</a>'
            )
        else:
            return ""

    website_link.allow_tags = True
    public_url.allow_tags = True


class LocationForm(forms.ModelForm):
    temp_image_url = forms.CharField(
        label="Image URL",
        required=False,
        help_text="will be shown when clicking on the location",
    )

    def save(self, commit=True):
        # Safe file to Google Cloud Storage
        temp_image_url = self.cleaned_data.get("temp_image_url", None)
        if temp_image_url:
            with requests.get(temp_image_url, stream=True) as r:
                # see https://stackoverflow.com/questions/57979304/ \
                # is-there-a-way-to-stream-data-directly-from-python-request-to-minio-bucket/59999799#59999799
                r.raw.seek = lambda x, y: 0
                r.raw.size = int(r.headers["Content-Length"])
                import uuid

                # @todo add support for other image types
                filename = uuid.uuid4().hex.upper()[0:10] + ".jpeg"
                self.instance.header_photo.save(filename, r.raw, save=True)

        return super(LocationForm, self).save(commit=commit)

    class Meta:
        model = Location
        fields = "__all__"


class LocationIsVerifiedFilter(admin.SimpleListFilter):
    title = "is Verified"
    parameter_name = "is_verified"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(verified_at__isnull=False)
        elif self.value() == "no":
            return queryset.filter(verified_at__isnull=True)


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    form = LocationForm
    formfield_overrides = {
        map_fields.AddressField: {"widget": map_widgets.GoogleMapsAddressWidget},
    }
    list_display = ["city", "water_name", "country", "verified_at", "image_display"]
    list_filter = [LocationIsVerifiedFilter, "country"]
    search_fields = ["city", "country"]
    readonly_fields = ("image_display",)
    actions = ["verify_locations", "unverify_locations", "process_unverified_locations"]

    def verify_locations(self, request, queryset):
        updated = queryset.update(verified_at=timezone.now())
        self.message_user(
            request, f"{updated} location(s) were successfully marked as verified."
        )

    verify_locations.short_description = "Mark selected locations as verified"

    def unverify_locations(self, request, queryset):
        updated = queryset.update(verified_at=None)
        self.message_user(
            request, f"{updated} location(s) were successfully marked as unverified."
        )

    unverify_locations.short_description = "Mark selected locations as unverified"

    def process_unverified_locations(self, request, queryset):
        """Process selected unverified locations to add coordinates and header images asynchronously"""
        from .tasks import verify_locations_async

        # Filter to only unverified locations
        unverified = queryset.filter(verified_at__isnull=True)
        if not unverified:
            self.message_user(
                request, "No unverified locations were selected.", level="WARNING"
            )
            return

        # Get location IDs
        location_ids = list(unverified.values_list("id", flat=True))

        # Submit the task to Django Q
        task_id = async_task(
            verify_locations_async,
            location_ids=location_ids,
            dry_run=False,
            hook="app.tasks_hooks.location_verification_hook",
        )

        # Show message to user
        self.message_user(
            request,
            f"Processing {unverified.count()} locations asynchronously. Task ID: {task_id}",
            level="INFO",
        )

    process_unverified_locations.short_description = (
        "Process selected unverified locations"
    )

    def image_display(self, obj):
        if obj.header_photo:
            return mark_safe(
                '<div style="display:inline-block;width:300px;height:100px;'
                "background-image:url(%s);background-position: center;"
                'background-size: cover;"></div>' % (obj.header_photo.url)
            )
        else:
            return ""

    image_display.short_description = "Image"


class RaceInline(admin.TabularInline):
    model = Race
    exclude = ["coordinates"]
    fields = [
        "id",
        "date",
        "race_time",
        "distance",
        "name",
        "has_coordinates",
        "wetsuit",
        "price",
    ]
    readonly_fields = ["id", "has_coordinates"]

    def has_coordinates(self, obj: Race):
        return obj.coordinates is not None


class ReviewInline(admin.TabularInline):
    model = Review
    fields = ["created_at", "user", "rating", "comment"]
    readonly_fields = ["user", "created_at"]
    extra = 1

    formfield_overrides = {
        TextField: {"widget": Textarea(attrs={"rows": 1, "cols": 80})},
    }


class IsUpcomingFilter(admin.SimpleListFilter):
    title = "is upcoming"

    parameter_name = "is_upcoming"

    def lookups(self, request, model_admin):
        return (("yes", "Yes"),)

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(date_start__gt=datetime.now())


class IsVerifiedFilter(admin.SimpleListFilter):
    title = "is Verified"

    parameter_name = "is_verified"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(verified_at__isnull=False)
        elif self.value() == "no":
            return queryset.filter(verified_at__isnull=True)


class CrawlSingleEventForm(forms.Form):
    """Form for crawling a single event asynchronously"""

    url = forms.URLField(
        widget=forms.URLInput(attrs={"size": 80}),
        help_text="Enter the URL of the event to crawl",
    )
    dry_run = forms.BooleanField(
        required=False,
        initial=False,
        help_text="Check to perform a dry run without saving to the database",
    )


@admin.register(models.Event)
class EventAdmin(CloneModelAdmin):
    list_per_page = 30
    list_display = (
        "date_start",
        "eventstr",
        "locationstr",
        "entry_quality",
        "verified_at",
    )
    list_display_links = ("eventstr",)
    list_filter = (
        IsUpcomingFilter,
        "entry_quality",
        IsVerifiedFilter,
        "created_by",
        ("organizer", RelatedDropdownFilter),
        "location__country",
    )
    search_fields = ["name", "location__city", "location__country", "organizer__name"]
    exclude = ["edited_by", "edited_at"]
    readonly_fields = ["public_url", "created_by"]
    inlines = [RaceInline, ReviewInline]
    date_hierarchy = "date_start"
    prepopulated_fields = {"slug": ("name", "date_start")}

    # Add custom actions
    actions = []

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        my_urls = [
            path(
                "crawl-single-event/",
                self.admin_site.admin_view(self.crawl_single_event_view),
                name="app_event_crawl_single",
            ),
        ]
        return my_urls + urls

    def crawl_single_event_view(self, request):
        """Custom view to crawl a single event asynchronously"""
        from .tasks import crawl_single_event_async

        if request.method == "POST":
            form = CrawlSingleEventForm(request.POST)
            if form.is_valid():
                url = form.cleaned_data["url"]
                dry_run = form.cleaned_data["dry_run"]

                # Submit the task to Django Q
                task_id = async_task(
                    crawl_single_event_async,
                    url=url,
                    dry_run=dry_run,
                    hook="app.tasks_hooks.crawl_single_event_hook",
                )

                # Show message to user
                self.message_user(
                    request,
                    f"Crawling event from URL: {url} asynchronously. Task ID: {task_id}",
                    level="INFO",
                )
                return HttpResponseRedirect("../")
        else:
            form = CrawlSingleEventForm()

        # Render the form
        context = {
            "title": "Crawl Single Event",
            "form": form,
            "opts": self.model._meta,
            "media": self.media,
        }
        return render(request, "admin/crawl_single_event.html", context)

    class Media:
        js = ("js/admin/EventAdmin.js",)

    def changelist_view(self, request, extra_context=None):
        if request.GET:
            return super().changelist_view(request, extra_context=extra_context)

        url = "{}??date_start__year=2021".format(request.path)
        from django.shortcuts import redirect

        return redirect(url)

    def eventstr(self, obj: Event):
        if obj.invisible:
            style = "color:#999"
        elif obj.cancelled:
            style = "color:#a00"
        else:
            style = ""
        return format_html(f'<span style="{style}">{obj.name}</span>')

    def locationstr(self, obj):
        if obj.location:
            return f"{obj.location.city}, {obj.location.country}"

    def entry_quality(self, obj):
        rating = obj.get_quality_rating()
        if rating < 25:
            color = "rgba(244, 0, 0, 0.5)"
        elif rating < 30:
            color = "rgba(244, 122, 0, 0.5)"
        else:
            color = "rgba(0, 255, 122, 0.5)"

        return format_html(
            f'<span style="background-color: {color};'
            f'padding:2px">'
            f"{obj.get_quality_rating()}</span>"
        )

    def public_url(self, obj):
        url = settings.FRONTEND_URL + "?" + urlencode({"event": obj.slug})
        return format_html(f'<a target="_blank" href="{url}">{url}</a>')

    public_url.allow_tags = True
