from django.db.models.signals import pre_save

from app.models import Review


def update_location_rating(sender, instance: Review, **kwargs):
    """ Update location rating whenever a review is saved """
    instance.event.location.update_average_rating()


pre_save.connect(update_location_rating, sender=Review)
