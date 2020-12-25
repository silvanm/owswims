import requests
from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields
from . import models
from .models import Race, Event, Location

admin.site.site_header = ugettext_lazy('Open-Water-Swims Admin')

admin.site.register(models.Organizer)


class LocationForm(forms.ModelForm):
    temp_image_url = forms.CharField(label='Image URL',
                                     required=False,
                                     help_text='will be shown when clicking on the location',
                                     )

    def save(self, commit=True):
        # Safe file to Google Cloud Storage
        temp_image_url = self.cleaned_data.get('temp_image_url', None)
        if (temp_image_url):
            with requests.get(temp_image_url, stream=True) as r:
                # see https://stackoverflow.com/questions/57979304/ \
                # is-there-a-way-to-stream-data-directly-from-python-request-to-minio-bucket/59999799#59999799
                r.raw.seek = lambda x, y: 0
                r.raw.size = int(r.headers["Content-Length"])
                import uuid
                # @todo add support for other image types
                filename=uuid.uuid4().hex.upper()[0:10] + '.jpeg'
                self.instance.header_photo.save(filename, r.raw, save=True)

        return super(LocationForm, self).save(commit=commit)

    class Meta:
        model = Location
        fields = '__all__'


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    form = LocationForm
    formfield_overrides = {
        map_fields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},
    }
    list_display = ['city', 'country', 'image_display']
    search_fields = ['city', 'country']
    readonly_fields = ('image_display',)

    def image_display(self, obj):
        if obj.header_photo:
            return mark_safe('<div style="display:inline-block;width:300px;height:100px;'
                             'background-image:url(%s);background-position: center;'
                             'background-size: cover;"></div>' % (obj.header_photo.url))
        else:
            return ''

    image_display.short_description = 'Image'


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
    search_fields = ['name', 'location__city', 'location__country', 'organizer__name']
    exclude = ["edited_by", "edited_at"]
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
