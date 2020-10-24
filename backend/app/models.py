from django.db import models
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
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)

    def __repr__(self):
        return repr(f"({self.id}) {self.name}, {self.location}")


class Race(models.Model):
    """
    Represents a single race at one event
    """

    date = models.DateField()
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    distance = models.FloatField(verbose_name="Distance (km)")
    name = models.CharField(max_length=30, null=True)

    def __repr__(self):
        return repr(f"({self.id}) {self.distance}")
