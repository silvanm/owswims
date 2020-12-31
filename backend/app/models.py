from datetime import date

from crum import get_current_request, get_current_user
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField
from django_google_maps import fields as map_fields


class Location(models.Model):
    city = models.CharField(max_length=50)
    country = CountryField()
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    address = map_fields.AddressField(max_length=200, default=None, null=True, blank=True)
    header_photo = models.ImageField(upload_to='photos', null=True, blank=True)

    class Meta:
        ordering = ["city"]

    def __str__(self):
        return repr(f"{self.city}, {self.country}")


class Organizer(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField(max_length=200)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return repr(f"{self.name}")


class Event(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField(max_length=200, blank=True)
    flyer_image = models.ImageField(upload_to='flyers', null=True, blank=True,
                                    help_text="Flyer or poster showing event details")
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, null=True, related_name="events"
    )
    organizer = models.ForeignKey(
        Organizer,
        on_delete=models.SET_NULL,
        null=True,
        related_name="events",
        blank=True,
    )
    needs_medical_certificate = models.BooleanField(null=True, blank=True)
    needs_license = models.BooleanField(null=True, blank=True)
    sold_out = models.BooleanField(null=True, blank=True)
    cancelled = models.BooleanField(null=True, blank=True, default=False)
    invisible = models.BooleanField(null=True, blank=True, default=False,
                                    help_text="Hidden from public")
    with_ranking = models.BooleanField(null=True, blank=True)
    date_start = models.DateField()
    date_end = models.DateField()
    water_temp = models.FloatField(null=True, blank=True)
    description = models.TextField(max_length=2048, default="", blank=True,
                                   help_text='Comment shown to the public')
    internal_comment = models.TextField(max_length=2048, default="", blank=True,
                                        help_text='Comment NOT shown to the public')
    entry_quality = models.CharField(
        max_length=10,
        choices=[("incomplete", "Incomplete"), ("complete", "Complete")],
        null=True,
        blank=True,
    )
    water_type = models.CharField(
        max_length=10,
        choices=[("river", "River"), ("sea", "Sea"), ("lake", "Lake"), ("pool", "Pool")],
        null=True,
        blank=True,
    )
    source = models.CharField(max_length=30, null=True, blank=True)
    edited_by = models.ForeignKey(User, null=True, help_text='Author who has done the last edit',
                                  on_delete=models.SET_NULL)
    edited_at = models.DateTimeField(null=True, help_text='Timestamp of the last edit')
    verified_at = models.DateTimeField(
        null=True, blank=True, help_text="set if the event has been verified by the admin"
    )

    class Meta:
        ordering = ["date_start"]

    def is_verified(self):
        return self.verified_at is not None

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        self.edited_by = user
        self.edited_at = timezone.now()
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return repr(f"{self.date_start}, {self.name}, {self.location}")


class Race(models.Model):
    """
    Represents a single race at one event
    """

    date = models.DateField(help_text="Date of event, in local time")
    race_time = models.TimeField(help_text="Date and time of event, in local time", default=None, blank=True, null=True)
    event = models.ForeignKey("Event", related_name="races", on_delete=models.CASCADE)
    distance = models.FloatField(verbose_name="Distance (km)")
    name = models.CharField(max_length=30, null=True, blank=True)
    wetsuit = models.CharField(
        max_length=10,
        choices=[
            ("compulsory", "Compulsory"),
            ("optional", "Optional"),
            ("prohibited", "Prohibited"),
        ],
        null=True,
        blank=True,
    )
    price = MoneyField(
        max_digits=14, decimal_places=2, default_currency="EUR", null=True, blank=True
    )

    class Meta:
        ordering = ["distance"]

    def __str__(self):
        return repr(f"{self.event.name}, {self.distance}")
