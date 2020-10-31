import django_filters
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
        }
        include = (
            "name",
            "website",
            "location",
            "races",
        )
        interfaces = (Node,)

    # start_date = graphene.Date()
    # end_date = graphene.Date()


class EventNodeFilter(django_filters.FilterSet):
    race_distance_gte = django_filters.NumberFilter(
        field_name="races", lookup_expr="distance__gte", distinct=True
    )
    race_distance_lte = django_filters.NumberFilter(
        field_name="races", lookup_expr="distance__lte", distinct=True
    )
    date_from = django_filters.DateFilter(
        field_name="date_start", lookup_expr="gte", distinct=True
    )
    date_to = django_filters.DateFilter(
        field_name="date_end", lookup_expr="lte", distinct=True
    )

    class Meta:
        model = Event
        fields = (
            "date_from",
            "date_to",
            "name",
            "website",
            "location",
            "races",
        )


class Query(graphene.ObjectType):
    location = relay.Node.Field(LocationNode)
    all_locations = DjangoFilterConnectionField(LocationNode)

    event = relay.Node.Field(EventNode)
    all_events = DjangoFilterConnectionField(EventNode, filterset_class=EventNodeFilter)


schema = graphene.Schema(query=Query)
