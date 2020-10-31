from datetime import date

from django.db import models
from django.db.models import Max, Min
from django_countries.fields import CountryField


class Location(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    country = CountryField()
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)

    def __repr__(self):
        return repr(f"({self.id}) {self.city}, {self.country}")


class Event(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, related_name="events")
    date_start = models.DateField()
    date_end = models.DateField()

    # @property
    # def start_date(self) -> date:
    #     return self.race_set.all().aggregate(Min('date'))['date__min']
    #
    # @property
    # def end_date(self) -> date:
    #     return self.race_set.all().aggregate(Max('date'))['date__max']

    def __repr__(self):
        return repr(f"({self.id}) {self.name}, {self.location}")


class Race(models.Model):
    """
    Represents a single race at one event
    """

    date = models.DateField()
    event = models.ForeignKey("Event", related_name="races", on_delete=models.CASCADE)
    distance = models.FloatField(verbose_name="Distance (km)")
    name = models.CharField(max_length=30, null=True)

    def __repr__(self):
        return repr(f"({self.id}) {self.distance}")
