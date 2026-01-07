from django.core.cache import cache
from django.db.models.signals import pre_save, post_save, post_delete

from app.models import Review, Event


def update_location_rating(sender, instance: Review, **kwargs):
    """ Update location rating whenever a review is saved """
    instance.event.location.update_average_rating()


def clear_graphql_cache(sender, instance, **kwargs):
    """Clear GraphQL cache when Event is modified"""
    cache.clear()


pre_save.connect(update_location_rating, sender=Review)

post_save.connect(clear_graphql_cache, sender=Event)
post_delete.connect(clear_graphql_cache, sender=Event)
