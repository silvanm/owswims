import logging

import graphene
from graphene import relay
from graphql_auth import mutations
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from app.models import Event, Location, Race, Review, ApiToken
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
        id = graphene.ID(required=True)
        coordinates = graphene.List(graphene.Float, required=False)
        distance = graphene.Float(required=False)
        race_time = graphene.Time(required=False)
        name = graphene.String(required=False)
        wetsuit = graphene.String(required=False)
        price_value = graphene.Float(required=False)
        price_currency = graphene.String(required=False)

    race = graphene.Field(RaceNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, id, client_mutation_id=None, **kwargs):
        race = Race.objects.get(pk=from_global_id(id)[1])

        # Update coordinates if provided
        if "coordinates" in kwargs:
            coordinates = kwargs.get("coordinates")
            race.coordinates = [
                coordinates[i : i + 2] for i in range(0, len(coordinates), 2)
            ]

        # Update distance if provided
        if "distance" in kwargs:
            race.distance = kwargs.get("distance")

        # Update race_time if provided
        if "race_time" in kwargs:
            race.race_time = kwargs.get("race_time")

        # Update name if provided
        if "name" in kwargs:
            race.name = kwargs.get("name")

        # Update wetsuit if provided
        if "wetsuit" in kwargs:
            race.wetsuit = kwargs.get("wetsuit")

        # Update price if both currency and value are provided
        if "price_value" in kwargs and "price_currency" in kwargs:
            from djmoney.money import Money

            race.price = Money(kwargs.get("price_value"), kwargs.get("price_currency"))
        elif "price_value" in kwargs:
            # Only update value, keep existing currency
            from djmoney.money import Money

            race.price = Money(kwargs.get("price_value"), race.price_currency)
        elif "price_currency" in kwargs:
            # Only update currency, keep existing value
            from djmoney.money import Money

            race.price = Money(race.price.amount, kwargs.get("price_currency"))

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
            recipients=["silvan@open-water-swims.com"],
            html=message,
            from_email="silvan.muehlemann@muehlemann-popp.ch",
            subject=f"Mail from {sender}",
        )
        ok = response["total_accepted_recipients"]
        id = response["id"]
        return ContactMail(id=id, ok=ok)


class RateEvent(graphene.Mutation):
    class Arguments:
        event_id = graphene.ID(required=True)
        rating = graphene.Int(required=True)
        comment = graphene.String(required=False)
        name = graphene.String(required=False)
        country = graphene.String(required=False)

    success = graphene.Boolean()
    id = graphene.Int()

    def mutate(root, info, event_id, rating, comment=None, name=None, country=None):
        logging.info((event_id, rating, comment))
        event = Event.objects.get(pk=from_global_id(event_id)[1])
        rating = Review.objects.create(
            event=event,
            user=None,
            rating=rating,
            comment=comment,
            name=name,
            country=country,
        )
        success = True
        return RateEvent(success=success, id=rating.id)


class CreateApiToken(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    success = graphene.Boolean()
    token = graphene.String()
    error = graphene.String()

    @classmethod
    @login_required
    def mutate(cls, root, info, name):
        user = info.context.user

        # Create a new API token for the user
        try:
            api_token = ApiToken.objects.create(user=user, name=name)
            return CreateApiToken(success=True, token=api_token.token, error=None)
        except Exception as e:
            return CreateApiToken(success=False, token=None, error=str(e))


class DeleteApiToken(graphene.Mutation):
    class Arguments:
        token_id = graphene.ID(required=True)

    success = graphene.Boolean()
    error = graphene.String()

    @classmethod
    @login_required
    def mutate(cls, root, info, token_id):
        user = info.context.user

        try:
            # Get the token and check if it belongs to the user
            token = ApiToken.objects.get(id=from_global_id(token_id)[1])

            if token.user != user:
                return DeleteApiToken(
                    success=False,
                    error="You don't have permission to delete this token",
                )

            # Delete the token
            token.delete()
            return DeleteApiToken(success=True, error=None)
        except ApiToken.DoesNotExist:
            return DeleteApiToken(success=False, error="Token not found")
        except Exception as e:
            return DeleteApiToken(success=False, error=str(e))


class Mutation(AuthMutation, graphene.ObjectType):
    update_event = EventMutation.Field()
    update_location = LocationMutation.Field()
    update_race = RaceMutation.Field()
    send_contactmail = ContactMail.Field()
    rate_event = RateEvent.Field()
    create_api_token = CreateApiToken.Field()
    delete_api_token = DeleteApiToken.Field()
