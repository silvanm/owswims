from graphene_django import DjangoObjectType
import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField

from app.models import Location, Race, Event


class LocationNode(DjangoObjectType):
    class Meta:
        model = Location
        filter_fields = ["city", "country"]
        interfaces = (relay.Node,)


class RaceNode(DjangoObjectType):
    class Meta:
        model = Race
        filter_fields = ["date", "distance"]
        interfaces = (relay.Node,)


class EventNode(DjangoObjectType):
    class Meta:
        model = Event
        filter_fields = {
            "name": ["exact"],
            "website": ["exact"],
            "location": ["exact"],
            "location__country": ["exact"],
            "location__city": ["exact", "icontains"],
        }
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    location = relay.Node.Field(LocationNode)
    all_locations = DjangoFilterConnectionField(LocationNode)

    event = relay.Node.Field(EventNode)
    all_events = DjangoFilterConnectionField(EventNode)


schema = graphene.Schema(query=Query)
