from graphene_django import DjangoObjectType
import graphene
from graphene import relay, Node
from graphene_django.filter import DjangoFilterConnectionField

from app.models import Location, Race, Event


class LocationNode(DjangoObjectType):
    class Meta:
        model = Location
        filter_fields = ["city", "country"]
        interfaces = (Node,)


class RaceNode(DjangoObjectType):
    class Meta:
        model = Race
        filter_fields = ["date", "distance"]
        interfaces = (Node,)


class EventNode(DjangoObjectType):
    class Meta:
        model = Event
        filter_fields = {
            "name": ["exact"],
            "website": ["exact"],
            "location": ["exact"],
            "location__country": ["exact"],
            "location__city": ["exact", "icontains"],
            "races__date": ["lte", "gte"],
            "races__distance": ["lte", "gte"],
        }
        include = ("name", "website", "location", "races")
        interfaces = (Node,)
    # start_date = graphene.Date()
    # end_date = graphene.Date()



class Query(graphene.ObjectType):
    location = relay.Node.Field(LocationNode)
    all_locations = DjangoFilterConnectionField(LocationNode)

    event = relay.Node.Field(EventNode)
    all_events = DjangoFilterConnectionField(EventNode)


schema = graphene.Schema(query=Query)
