from datetime import date

from django.db import models
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField


class Location(models.Model):
    street = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    country = CountryField()
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

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
    date_start = models.DateField()
    date_end = models.DateField()
    water_temp = models.FloatField(null=True, blank=True)
    description = models.TextField(max_length=1024, default="", blank=True)
    water_type = models.CharField(
        max_length=10,
        choices=[("river", "River"), ("sea", "Sea"), ("lake", "Lake")],
        null=True,
        blank=True,
    )
    source = models.CharField(max_length=30, null=True, blank=True)
    verified_at = models.DateField(
        null=True, blank=True, help_text="set if the event has been verified by the admin"
    )

    class Meta:
        ordering = ["date_start"]

    def __str__(self):
        return repr(f"{self.date_start}, {self.name}, {self.location}")


class Race(models.Model):
    """
    Represents a single race at one event
    """

    date = models.DateField()
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
