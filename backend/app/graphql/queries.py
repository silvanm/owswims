import django_filters
import graphene
from django.db.models import Q
from graphene import Node, relay
from graphene_django import DjangoObjectType
from graphene_django.debug import DjangoDebug
from graphene_django.filter import DjangoFilterConnectionField
from graphql_auth.schema import UserQuery, MeQuery

from app.models import Organizer, Location, Race, Event


class OrganizerNode(DjangoObjectType):
    class Meta:
        model = Organizer
        include = ("__all__",)
        interfaces = (Node,)


def get_header_photo_url(obj, resolve_obj):
    if obj.header_photo:
        return obj.header_photo.url
    else:
        return None


class LocationNode(DjangoObjectType):
    class Meta:
        model = Location
        filter_fields = ["city", "country", "events"]
        fields = (
            "city",
            "water_type",
            "water_name",
            "country",
            "lat",
            "lng",
            "events",
            "header_photo",
        )
        interfaces = (Node,)

    # returns the URL of the header photo
    # see # see https://stackoverflow.com/questions/52767366/ \
    # how-can-i-resolve-custom-fields-for-django-models-using-django-graphene
    header_photo = graphene.String(resolver=get_header_photo_url)


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
        fields = ("city", "water_type", "water_name", "country", "lat", "lng", "events")


class RaceNode(DjangoObjectType):
    class Meta:
        model = Race
        filter_fields = {"distance": ["lte", "gte"]}
        fields = (
            "date",
            "race_time",
            "name",
            "distance",
            "wetsuit",
            "price_value",
            "price_currency",
            "coordinates",
        )
        interfaces = (Node,)

    price_value = graphene.String(resolver=lambda obj, resolve_obj: str(obj.price))


def get_flyer_image_url(obj, resolve_obj):
    if obj.flyer_image:
        return obj.flyer_image.url
    else:
        return None


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
        include = "__all__"
        interfaces = (Node,)

    flyer_image = graphene.String(resolver=get_flyer_image_url)


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
            "slug",
        )


class Query(UserQuery, MeQuery, graphene.ObjectType):
    location = relay.Node.Field(LocationNode)
    all_locations = DjangoFilterConnectionField(
        LocationNode, filterset_class=LocationNodeFilter
    )
    debug = graphene.Field(DjangoDebug, name="_debug")

    event = relay.Node.Field(EventNode)
    all_events = DjangoFilterConnectionField(EventNode, filterset_class=EventNodeFilter)

    race = relay.Node.Field(RaceNode)

    # Not GraphQL style, but leads to fast query not returning dates without
    # events
    locations_filtered = graphene.List(
        LocationNode,
        date_from=graphene.Date(),
        date_to=graphene.Date(),
        race_distance_gte=graphene.Float(),
        race_distance_lte=graphene.Float(),
        keyword=graphene.String(),
        event_slug=graphene.String(),
    )

    def resolve_locations_filtered(
        root, info, race_distance_gte, race_distance_lte, date_from, date_to, keyword=""
    ):
        q = Q(
            events__races__distance__gte=race_distance_gte,
            events__races__distance__lte=race_distance_lte,
            events__date_start__gte=date_from,
            events__date_start__lte=date_to,
            events__invisible=False,
        )

        if len(keyword) >= 3:
            q = q & (
                Q(events__name__istartswith=keyword) | Q(city__istartswith=keyword)
            )

        return Location.objects.filter(q).distinct().all()

    organizer = relay.Node.Field(OrganizerNode)
