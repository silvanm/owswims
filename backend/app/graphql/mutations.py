import logging

import graphene
from graphene import relay
from graphql_auth import mutations
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from app.models import Event, Location, Race, Review
from .queries import LocationNode, RaceNode, EventNode


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
    @login_required
    def mutate_and_get_payload(cls, root, info, city, id, client_mutation_id=None):
        location = Location.objects.get(pk=from_global_id(id)[1])
        location.city = city
        location.save()
        return LocationMutation(location=location)


class RaceMutation(relay.ClientIDMutation):
    class Input:
        coordinates = graphene.List(graphene.Float, required=True)
        id = graphene.ID()

    race = graphene.Field(RaceNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(
            cls, root, info, coordinates, id, client_mutation_id=None
    ):
        race = Race.objects.get(pk=from_global_id(id)[1])
        race.coordinates = [
            coordinates[i: i + 2] for i in range(0, len(coordinates), 2)
        ]
        race.save()
        return RaceMutation(race=race)


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()


class ContactMail(graphene.Mutation):
    class Arguments:
        sender = graphene.String(required=True)
        message = graphene.String(required=True)

    ok = graphene.Boolean()
    id = graphene.String()

    def mutate(root, info, sender, message):
        from sparkpost import SparkPost
        sp = SparkPost()

        response = sp.transmissions.send(
            recipients=['silvan@open-water-swims.com'],
            html=message,
            from_email='silvan.muehlemann@muehlemann-popp.ch',
            subject=f'Mail from {sender}'
        )
        ok = response['total_accepted_recipients']
        id = response['id']
        return ContactMail(id=id, ok=ok)


class RateEvent(graphene.Mutation):
    class Arguments:
        event_id = graphene.ID(required=True)
        rating = graphene.Int(required=True)
        comment = graphene.String(required=False)

    success = graphene.Boolean()
    id = graphene.Int()

    def mutate(root, info, event_id, rating, comment=None):
        logging.info((event_id, rating, comment))
        event = Event.objects.get(pk=from_global_id(event_id)[1])
        rating = Review.objects.create(event=event, user=None, rating=rating, comment=comment)
        success = True
        return RateEvent(success=success, id=rating.id)


class Mutation(AuthMutation, graphene.ObjectType):
    update_event = EventMutation.Field()
    update_location = LocationMutation.Field()
    update_race = RaceMutation.Field()
    send_contactmail = ContactMail.Field()
    rate_event = RateEvent.Field()
