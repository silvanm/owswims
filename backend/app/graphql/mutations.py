import logging

import graphene
from graphene import relay
from graphql_auth import mutations
from graphql_jwt.decorators import login_required
from graphql_relay import from_global_id

from app.models import Event, Location, Race, Review, ApiToken
from .queries import LocationNode, RaceNode, EventNode


class EventMutation(relay.ClientIDMutation):
    """Update an existing event with comprehensive field support"""

    class Input:
        id = graphene.ID(required=True)
        # Basic fields
        name = graphene.String(required=False)
        website = graphene.String(required=False)
        slug = graphene.String(required=False)
        description = graphene.String(required=False)
        internal_comment = graphene.String(required=False)
        # Date fields
        date_start = graphene.Date(required=False)
        date_end = graphene.Date(required=False)
        water_temp = graphene.Float(required=False)
        # Status fields
        needs_medical_certificate = graphene.Boolean(required=False)
        needs_license = graphene.Boolean(required=False)
        sold_out = graphene.Boolean(required=False)
        cancelled = graphene.Boolean(required=False)
        invisible = graphene.Boolean(required=False)
        with_ranking = graphene.Boolean(required=False)
        # Quality fields
        entry_quality = graphene.String(required=False)
        source = graphene.String(required=False)
        # Relationships
        location_id = graphene.ID(required=False)
        organizer_id = graphene.ID(required=False)
        previous_year_event_id = graphene.ID(required=False)

    event = graphene.Field(EventNode)

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, client_mutation_id=None, **kwargs):
        event = Event.objects.get(pk=from_global_id(id)[1])

        # Update basic fields
        if "name" in kwargs:
            event.name = kwargs.get("name")
        if "website" in kwargs:
            event.website = kwargs.get("website")
        if "slug" in kwargs:
            event.slug = kwargs.get("slug")
        if "description" in kwargs:
            event.description = kwargs.get("description")
        if "internal_comment" in kwargs:
            event.internal_comment = kwargs.get("internal_comment")

        # Update date fields
        if "date_start" in kwargs:
            event.date_start = kwargs.get("date_start")
        if "date_end" in kwargs:
            event.date_end = kwargs.get("date_end")
        if "water_temp" in kwargs:
            event.water_temp = kwargs.get("water_temp")

        # Update status fields
        if "needs_medical_certificate" in kwargs:
            event.needs_medical_certificate = kwargs.get("needs_medical_certificate")
        if "needs_license" in kwargs:
            event.needs_license = kwargs.get("needs_license")
        if "sold_out" in kwargs:
            event.sold_out = kwargs.get("sold_out")
        if "cancelled" in kwargs:
            event.cancelled = kwargs.get("cancelled")
        if "invisible" in kwargs:
            event.invisible = kwargs.get("invisible")
        if "with_ranking" in kwargs:
            event.with_ranking = kwargs.get("with_ranking")

        # Update quality fields
        if "entry_quality" in kwargs:
            entry_quality = kwargs.get("entry_quality")
            if entry_quality in ["incomplete", "complete"]:
                event.entry_quality = entry_quality
        if "source" in kwargs:
            event.source = kwargs.get("source")

        # Update relationships
        if "location_id" in kwargs:
            location_id = kwargs.get("location_id")
            if location_id:
                event.location = Location.objects.get(
                    pk=from_global_id(location_id)[1]
                )
            else:
                event.location = None

        if "organizer_id" in kwargs:
            organizer_id = kwargs.get("organizer_id")
            if organizer_id:
                from app.models import Organizer

                event.organizer = Organizer.objects.get(
                    pk=from_global_id(organizer_id)[1]
                )
            else:
                event.organizer = None

        if "previous_year_event_id" in kwargs:
            prev_id = kwargs.get("previous_year_event_id")
            if prev_id:
                event.previous_year_event = Event.objects.get(
                    pk=from_global_id(prev_id)[1]
                )
            else:
                event.previous_year_event = None

        event.save()
        return EventMutation(event=event)


class CreateEventMutation(relay.ClientIDMutation):
    """Create a new event"""

    class Input:
        # Required fields
        name = graphene.String(required=True)
        date_start = graphene.Date(required=True)
        date_end = graphene.Date(required=True)
        # Optional fields
        website = graphene.String(required=False)
        slug = graphene.String(required=False)
        description = graphene.String(required=False)
        internal_comment = graphene.String(required=False)
        water_temp = graphene.Float(required=False)
        needs_medical_certificate = graphene.Boolean(required=False)
        needs_license = graphene.Boolean(required=False)
        sold_out = graphene.Boolean(required=False)
        cancelled = graphene.Boolean(required=False)
        invisible = graphene.Boolean(required=False)
        with_ranking = graphene.Boolean(required=False)
        entry_quality = graphene.String(required=False)
        source = graphene.String(required=False)
        location_id = graphene.ID(required=False)
        organizer_id = graphene.ID(required=False)

    event = graphene.Field(EventNode)

    @classmethod
    def mutate_and_get_payload(
        cls, root, info, name, date_start, date_end, client_mutation_id=None, **kwargs
    ):
        # Create new event with required fields
        event = Event(name=name, date_start=date_start, date_end=date_end)

        # Set optional fields
        if "website" in kwargs:
            event.website = kwargs.get("website")
        if "slug" in kwargs:
            event.slug = kwargs.get("slug")
        if "description" in kwargs:
            event.description = kwargs.get("description")
        if "internal_comment" in kwargs:
            event.internal_comment = kwargs.get("internal_comment")
        if "water_temp" in kwargs:
            event.water_temp = kwargs.get("water_temp")
        if "needs_medical_certificate" in kwargs:
            event.needs_medical_certificate = kwargs.get("needs_medical_certificate")
        if "needs_license" in kwargs:
            event.needs_license = kwargs.get("needs_license")
        if "sold_out" in kwargs:
            event.sold_out = kwargs.get("sold_out")
        if "cancelled" in kwargs:
            event.cancelled = kwargs.get("cancelled")
        if "invisible" in kwargs:
            event.invisible = kwargs.get("invisible")
        if "with_ranking" in kwargs:
            event.with_ranking = kwargs.get("with_ranking")
        if "entry_quality" in kwargs:
            entry_quality = kwargs.get("entry_quality")
            if entry_quality in ["incomplete", "complete"]:
                event.entry_quality = entry_quality
        if "source" in kwargs:
            event.source = kwargs.get("source")

        # Set relationships
        if "location_id" in kwargs:
            location_id = kwargs.get("location_id")
            if location_id:
                event.location = Location.objects.get(
                    pk=from_global_id(location_id)[1]
                )

        if "organizer_id" in kwargs:
            organizer_id = kwargs.get("organizer_id")
            if organizer_id:
                from app.models import Organizer

                event.organizer = Organizer.objects.get(
                    pk=from_global_id(organizer_id)[1]
                )

        event.save()
        return CreateEventMutation(event=event)


class LocationMutation(relay.ClientIDMutation):
    """Update an existing location with comprehensive field support"""

    class Input:
        id = graphene.ID(required=True)
        # Basic fields
        city = graphene.String(required=False)
        country = graphene.String(required=False)
        water_name = graphene.String(required=False)
        water_type = graphene.String(required=False)
        # Geo fields
        lat = graphene.Float(required=False)
        lng = graphene.Float(required=False)
        address = graphene.String(required=False)

    location = graphene.Field(LocationNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, id, client_mutation_id=None, **kwargs):
        location = Location.objects.get(pk=from_global_id(id)[1])

        # Update basic fields
        if "city" in kwargs:
            location.city = kwargs.get("city")
        if "country" in kwargs:
            location.country = kwargs.get("country")
        if "water_name" in kwargs:
            location.water_name = kwargs.get("water_name")
        if "water_type" in kwargs:
            water_type = kwargs.get("water_type")
            if water_type in ["river", "sea", "lake", "pool"]:
                location.water_type = water_type

        # Update geo fields
        if "lat" in kwargs:
            location.lat = kwargs.get("lat")
        if "lng" in kwargs:
            location.lng = kwargs.get("lng")
        if "address" in kwargs:
            location.address = kwargs.get("address")

        location.save()
        return LocationMutation(location=location)


class CreateLocationMutation(relay.ClientIDMutation):
    """Create a new location"""

    class Input:
        # Required fields
        city = graphene.String(required=True)
        country = graphene.String(required=True)
        # Optional fields
        water_name = graphene.String(required=False)
        water_type = graphene.String(required=False)
        lat = graphene.Float(required=False)
        lng = graphene.Float(required=False)
        address = graphene.String(required=False)

    location = graphene.Field(LocationNode)

    @classmethod
    @login_required
    def mutate_and_get_payload(
        cls, root, info, city, country, client_mutation_id=None, **kwargs
    ):
        # Create new location with required fields
        location = Location(city=city, country=country)

        # Set optional fields
        if "water_name" in kwargs:
            location.water_name = kwargs.get("water_name")
        if "water_type" in kwargs:
            water_type = kwargs.get("water_type")
            if water_type in ["river", "sea", "lake", "pool"]:
                location.water_type = water_type
        if "lat" in kwargs:
            location.lat = kwargs.get("lat")
        if "lng" in kwargs:
            location.lng = kwargs.get("lng")
        if "address" in kwargs:
            location.address = kwargs.get("address")

        location.save()
        return CreateLocationMutation(location=location)


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


class CreateRaceMutation(relay.ClientIDMutation):
    """Create a new race for an event"""

    class Input:
        # Required fields
        event_id = graphene.ID(required=True)
        date = graphene.Date(required=True)
        distance = graphene.Float(required=True)
        # Optional fields
        race_time = graphene.Time(required=False)
        name = graphene.String(required=False)
        wetsuit = graphene.String(required=False)
        price_value = graphene.Float(required=False)
        price_currency = graphene.String(required=False)
        coordinates = graphene.List(graphene.Float, required=False)

    race = graphene.Field(RaceNode)

    @classmethod
    def mutate_and_get_payload(
        cls, root, info, event_id, date, distance, client_mutation_id=None, **kwargs
    ):
        # Get the event
        event = Event.objects.get(pk=from_global_id(event_id)[1])

        # Create new race with required fields
        race = Race(event=event, date=date, distance=distance)

        # Set optional fields
        if "race_time" in kwargs:
            race.race_time = kwargs.get("race_time")
        if "name" in kwargs:
            race.name = kwargs.get("name")
        if "wetsuit" in kwargs:
            wetsuit = kwargs.get("wetsuit")
            if wetsuit in ["compulsory", "optional", "prohibited"]:
                race.wetsuit = wetsuit
        if "coordinates" in kwargs:
            coordinates = kwargs.get("coordinates")
            race.coordinates = [
                coordinates[i : i + 2] for i in range(0, len(coordinates), 2)
            ]

        # Handle price
        if "price_value" in kwargs and "price_currency" in kwargs:
            from djmoney.money import Money

            race.price = Money(kwargs.get("price_value"), kwargs.get("price_currency"))
        elif "price_value" in kwargs:
            from djmoney.money import Money

            race.price = Money(kwargs.get("price_value"), "EUR")

        race.save()
        return CreateRaceMutation(race=race)


class OrganizerMutation(relay.ClientIDMutation):
    """Update an existing organizer"""

    class Input:
        id = graphene.ID(required=True)
        # Basic fields
        name = graphene.String(required=False)
        website = graphene.String(required=False)
        internal_comment = graphene.String(required=False)
        # Contact fields
        contact_email = graphene.String(required=False)
        contact_form_url = graphene.String(required=False)
        contact_status = graphene.String(required=False)
        contact_notes = graphene.String(required=False)

    organizer = graphene.Field("app.graphql.queries.OrganizerNode")

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, id, client_mutation_id=None, **kwargs):
        from app.models import Organizer

        organizer = Organizer.objects.get(pk=from_global_id(id)[1])

        # Update basic fields
        if "name" in kwargs:
            organizer.name = kwargs.get("name")
        if "website" in kwargs:
            organizer.website = kwargs.get("website")
        if "internal_comment" in kwargs:
            organizer.internal_comment = kwargs.get("internal_comment")

        # Update contact fields
        if "contact_email" in kwargs:
            organizer.contact_email = kwargs.get("contact_email")
        if "contact_form_url" in kwargs:
            organizer.contact_form_url = kwargs.get("contact_form_url")
        if "contact_status" in kwargs:
            contact_status = kwargs.get("contact_status")
            if contact_status in [
                "pending",
                "contacted",
                "responded",
                "completed",
                "failed",
                "needs_review",
            ]:
                organizer.contact_status = contact_status
        if "contact_notes" in kwargs:
            organizer.contact_notes = kwargs.get("contact_notes")

        organizer.save()
        return OrganizerMutation(organizer=organizer)


class CreateOrganizerMutation(relay.ClientIDMutation):
    """Create a new organizer"""

    class Input:
        # Required fields
        name = graphene.String(required=True)
        website = graphene.String(required=True)
        # Optional fields
        internal_comment = graphene.String(required=False)
        contact_email = graphene.String(required=False)
        contact_form_url = graphene.String(required=False)
        contact_status = graphene.String(required=False)
        contact_notes = graphene.String(required=False)

    organizer = graphene.Field("app.graphql.queries.OrganizerNode")

    @classmethod
    @login_required
    def mutate_and_get_payload(
        cls, root, info, name, website, client_mutation_id=None, **kwargs
    ):
        from app.models import Organizer

        # Create new organizer with required fields
        organizer = Organizer(name=name, website=website)

        # Set optional fields
        if "internal_comment" in kwargs:
            organizer.internal_comment = kwargs.get("internal_comment")
        if "contact_email" in kwargs:
            organizer.contact_email = kwargs.get("contact_email")
        if "contact_form_url" in kwargs:
            organizer.contact_form_url = kwargs.get("contact_form_url")
        if "contact_status" in kwargs:
            contact_status = kwargs.get("contact_status")
            if contact_status in [
                "pending",
                "contacted",
                "responded",
                "completed",
                "failed",
                "needs_review",
            ]:
                organizer.contact_status = contact_status
        if "contact_notes" in kwargs:
            organizer.contact_notes = kwargs.get("contact_notes")

        organizer.save()
        return CreateOrganizerMutation(organizer=organizer)


class DeleteRaceMutation(relay.ClientIDMutation):
    """Delete a race"""

    class Input:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    deleted_id = graphene.ID()

    @classmethod
    def mutate_and_get_payload(cls, root, info, id, client_mutation_id=None):
        try:
            race = Race.objects.get(pk=from_global_id(id)[1])
            race.delete()
            return DeleteRaceMutation(success=True, deleted_id=id)
        except Race.DoesNotExist:
            return DeleteRaceMutation(success=False, deleted_id=None)


class DeleteEventMutation(relay.ClientIDMutation):
    """Delete an event (WARNING: CASCADE deletes all races!)"""

    class Input:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    deleted_id = graphene.ID()

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, id, client_mutation_id=None):
        try:
            event = Event.objects.get(pk=from_global_id(id)[1])
            event.delete()
            return DeleteEventMutation(success=True, deleted_id=id)
        except Event.DoesNotExist:
            return DeleteEventMutation(success=False, deleted_id=None)


class DeleteLocationMutation(relay.ClientIDMutation):
    """Delete a location (WARNING: CASCADE deletes all events at this location!)"""

    class Input:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    deleted_id = graphene.ID()

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, id, client_mutation_id=None):
        try:
            location = Location.objects.get(pk=from_global_id(id)[1])
            location.delete()
            return DeleteLocationMutation(success=True, deleted_id=id)
        except Location.DoesNotExist:
            return DeleteLocationMutation(success=False, deleted_id=None)


class DeleteOrganizerMutation(relay.ClientIDMutation):
    """Delete an organizer (sets organizer to NULL on all events)"""

    class Input:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    deleted_id = graphene.ID()

    @classmethod
    @login_required
    def mutate_and_get_payload(cls, root, info, id, client_mutation_id=None):
        try:
            from app.models import Organizer

            organizer = Organizer.objects.get(pk=from_global_id(id)[1])
            organizer.delete()
            return DeleteOrganizerMutation(success=True, deleted_id=id)
        except Exception:
            return DeleteOrganizerMutation(success=False, deleted_id=None)


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
    # Event mutations
    update_event = EventMutation.Field()
    create_event = CreateEventMutation.Field()
    delete_event = DeleteEventMutation.Field()
    # Location mutations
    update_location = LocationMutation.Field()
    create_location = CreateLocationMutation.Field()
    delete_location = DeleteLocationMutation.Field()
    # Race mutations
    update_race = RaceMutation.Field()
    create_race = CreateRaceMutation.Field()
    delete_race = DeleteRaceMutation.Field()
    # Organizer mutations
    update_organizer = OrganizerMutation.Field()
    create_organizer = CreateOrganizerMutation.Field()
    delete_organizer = DeleteOrganizerMutation.Field()
    # Other mutations
    send_contactmail = ContactMail.Field()
    rate_event = RateEvent.Field()
    create_api_token = CreateApiToken.Field()
    delete_api_token = DeleteApiToken.Field()
