from datetime import datetime

from crum import get_current_user
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField
from django_google_maps import fields as map_fields
from model_clone import CloneMixin


class Location(models.Model):
    city = models.CharField(max_length=50)
    water_name = models.CharField(max_length=50, null=True, blank=True)
    water_type = models.CharField(
        max_length=10,
        choices=[("river", "River"), ("sea", "Sea"), ("lake", "Lake"), ("pool", "Pool")],
        null=True,
        blank=True,
    )
    country = CountryField()
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    address = map_fields.AddressField(max_length=200, default=None, null=True, blank=True)
    header_photo = models.ImageField(upload_to='photos', null=True, blank=True)

    class Meta:
        ordering = ["city"]

    def __str__(self):
        s = f"{self.water_name}, " if self.water_name else ""
        return s + f"{self.city}, {self.country}"


class Organizer(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField(max_length=200)
    logo = models.ImageField(upload_to='organizer_logo', null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True)
    internal_comment = models.TextField(max_length=10000, default="", blank=True,
                                        help_text='Comment NOT shown to the public')

    class Meta:
        ordering = ["name"]

    def number_of_events(self):
        return len(self.events.filter(date_start__gte=datetime.now()))

    def __str__(self):
        return f"{self.name}"


class Event(CloneMixin, models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField(max_length=200, blank=True)
    slug = models.SlugField(max_length=100, null=True)
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
    source = models.CharField(max_length=30, null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, help_text='Author who has created the event',
                                   on_delete=models.SET_NULL, related_name='created_event')
    created_at = models.DateTimeField(null=True)
    edited_by = models.ForeignKey(User, null=True, help_text='Author who has done the last edit',
                                  on_delete=models.SET_NULL, related_name='edited_event')
    edited_at = models.DateTimeField(null=True, auto_now=True, help_text='Timestamp of the last edit')
    verified_at = models.DateTimeField(
        null=True, blank=True, help_text="set if the event has been verified by the admin"
    )

    _clone_many_to_one_or_one_to_many_fields = ['races']

    class Meta:
        ordering = ["date_start"]

    def is_verified(self):
        return self.verified_at is not None

    def get_quality_rating(self):
        from app.services import EventChecker
        checker = EventChecker(self)
        return checker.get_rating()

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and not user.pk:
            user = None
        self.edited_by = user
        self.edited_at = timezone.now()
        if not self.id:
            self.created_by = user
            self.created_at = timezone.now()

        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return repr(f"{self.date_start}, {self.name}, {self.location}")


class Race(CloneMixin, models.Model):
    """
    Represents a single race at one event
    """

    date = models.DateField(help_text="Date of event, in local time")
    race_time = models.TimeField(help_text="Date and time of event, in local time", default=None, blank=True, null=True)
    event = models.ForeignKey("Event", related_name="races", on_delete=models.CASCADE)
    distance = models.FloatField(verbose_name="Distance (km)")
    coordinates = ArrayField(
        ArrayField(
            models.FloatField(),
            size=2,
        ),
        null=True,
        blank=True,
        help_text="Coordinates (lat/lng) of track"
    )
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
        ordering = ["date", "race_time", "distance"]

    def __str__(self):
        return repr(f"{self.event.name}, {self.distance}")


class Review(models.Model):
    """
    Represents a single review or rating
    """

    created_at = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey("Event", related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(null=True, validators=[MaxValueValidator(5), MinValueValidator(1)])
    comment = models.TextField(max_length=1024, null=True, blank=True)
    name = models.TextField(max_length=100, null=True, blank=True)
    country = CountryField(help_text='Country of origin of author', null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return repr(f"{self.rating}, {self.comment}")
