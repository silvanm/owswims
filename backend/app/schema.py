import django_filters
from graphene_django import DjangoObjectType
import graphene
from graphene import relay, Node
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay import from_global_id

from app.models import Location, Race, Event


class LocationNode(DjangoObjectType):
    class Meta:
        model = Location
        filter_fields = ["city", "country", "events"]
        interfaces = (Node,)


class LocationNodeFilter(django_filters.FilterSet):
    race_distance_gte = django_filters.NumberFilter(
        field_name="events", lookup_expr="races__distance__gte", distinct=True
    )
    race_distance_lte = django_filters.NumberFilter(
        field_name="events", lookup_expr="races__distance__lte", distinct=True
    )
    date_from = django_filters.DateFilter(
        field_name="events", lookup_expr="date_start__gte", distinct=True
    )
    date_to = django_filters.DateFilter(
        field_name="events", lookup_expr="date_start__lte", distinct=True
    )

    class Meta:
        model = Location
        fields = ("city", "country", "lat", "lng", "events")


class RaceNode(DjangoObjectType):
    class Meta:
        model = Race
        filter_fields = {"distance": ["lte", "gte"]}
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
            "date_start": ["lte", "gte"],
            "date_end": ["lte", "gte"],
        }
        include = (
            "name",
            "website",
            "location",
            "races",
        )
        interfaces = (Node,)


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
    all_locations = DjangoFilterConnectionField(
        LocationNode, filterset_class=LocationNodeFilter
    )

    event = relay.Node.Field(EventNode)
    all_events = DjangoFilterConnectionField(EventNode, filterset_class=EventNodeFilter)


class EventMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        id = graphene.ID()

    event = graphene.Field(EventNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, name, id, client_mutation_id=None):
        event = Event.objects.get(pk=from_global_id(id)[1])
        event.name = name
        event.save()
        return EventMutation(event=event)


class LocationMutation(relay.ClientIDMutation):
    class Input:
        city = graphene.String(required=True)
        id = graphene.ID()

    location = graphene.Field(LocationNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, city, id, client_mutation_id=None):
        location = Location.objects.get(pk=from_global_id(id)[1])
        location.city = city
        location.save()
        return LocationMutation(location=location)


class Mutation(graphene.ObjectType):
    update_event = EventMutation.Field()
    update_location = LocationMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
