#!/usr/bin/env python
"""
Interactive GraphQL Mutation Test Script
Tests all newly implemented mutations for the owswims project.
"""

import os
import sys
import django
import getpass
import json
from datetime import date, time

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "owswims.settings")
django.setup()

from django.contrib.auth import authenticate
from django.test import RequestFactory
from graphene.test import Client
from app.graphql.schema import schema


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")


def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")


def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def authenticate_user():
    """Authenticate user and return user object"""
    print_header("Authentication")
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    from django.contrib.auth.models import User

    user = authenticate(username=username, password=password)
    if user:
        print_success(f"Authenticated as {username}")
        return user
    else:
        print_error("Authentication failed")
        sys.exit(1)


def create_mock_request(user):
    """Create a mock request with authenticated user"""
    factory = RequestFactory()
    request = factory.post("/graphql")
    request.user = user
    return request


def run_mutation(client, mutation, variables, description, context=None):
    """Run a GraphQL mutation and display results"""
    print_info(f"Testing: {description}")
    try:
        result = client.execute(
            mutation,
            variables=variables,
            context_value=context
        )

        if result.get("errors"):
            print_error(f"Error: {result['errors']}")
            return None
        else:
            print_success("Success!")
            return result.get("data")
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None


def test_location_mutations(client, context):
    """Test Location create, update, delete mutations"""
    print_header("Testing Location Mutations")

    # 1. Create Location
    create_mutation = """
    mutation CreateLocation($input: CreateLocationMutationInput!) {
        createLocation(input: $input) {
            location {
                id
                city
                country
                waterName
                waterType
                lat
                lng
            }
        }
    }
    """

    variables = {
        "input": {
            "city": "Test City",
            "country": "CH",
            "waterName": "Test Lake",
            "waterType": "lake",
            "lat": 47.3769,
            "lng": 8.5417,
        }
    }

    result = run_mutation(
        client, create_mutation, variables, "Create Location", context
    )
    if not result:
        return None

    location_id = result["createLocation"]["location"]["id"]
    print(f"   Created Location ID: {location_id}")

    # 2. Update Location
    update_mutation = """
    mutation UpdateLocation($input: LocationMutationInput!) {
        updateLocation(input: $input) {
            location {
                id
                city
                waterName
            }
        }
    }
    """

    variables = {
        "input": {
            "id": location_id,
            "city": "Updated Test City",
            "waterName": "Updated Lake",
        }
    }

    run_mutation(client, update_mutation, variables, "Update Location", context)

    return location_id


def test_organizer_mutations(client, context):
    """Test Organizer create, update, delete mutations"""
    print_header("Testing Organizer Mutations")

    # 1. Create Organizer
    create_mutation = """
    mutation CreateOrganizer($input: CreateOrganizerMutationInput!) {
        createOrganizer(input: $input) {
            organizer {
                id
                name
                website
                slug
            }
        }
    }
    """

    variables = {
        "input": {
            "name": "Test Organizer",
            "website": "https://test-organizer.com",
            "contactEmail": "test@test-organizer.com",
        }
    }

    result = run_mutation(
        client, create_mutation, variables, "Create Organizer", context
    )
    if not result:
        return None

    organizer_id = result["createOrganizer"]["organizer"]["id"]
    print(f"   Created Organizer ID: {organizer_id}")

    # 2. Update Organizer
    update_mutation = """
    mutation UpdateOrganizer($input: OrganizerMutationInput!) {
        updateOrganizer(input: $input) {
            organizer {
                id
                name
                website
            }
        }
    }
    """

    variables = {
        "input": {
            "id": organizer_id,
            "name": "Updated Test Organizer",
            "contactStatus": "contacted",
        }
    }

    run_mutation(client, update_mutation, variables, "Update Organizer", context)

    return organizer_id


def test_event_mutations(client, location_id, organizer_id, context):
    """Test Event create, update, delete mutations"""
    print_header("Testing Event Mutations")

    # 1. Create Event
    create_mutation = """
    mutation CreateEvent($input: CreateEventMutationInput!) {
        createEvent(input: $input) {
            event {
                id
                name
                dateStart
                dateEnd
                location {
                    id
                    city
                }
                organizer {
                    id
                    name
                }
            }
        }
    }
    """

    variables = {
        "input": {
            "name": "Test Swimming Event",
            "dateStart": str(date.today()),
            "dateEnd": str(date.today()),
            "locationId": location_id,
            "organizerId": organizer_id,
            "website": "https://test-event.com",
            "description": "This is a test event",
        }
    }

    result = run_mutation(client, create_mutation, variables, "Create Event", context)
    if not result:
        return None

    event_id = result["createEvent"]["event"]["id"]
    print(f"   Created Event ID: {event_id}")

    # 2. Update Event
    update_mutation = """
    mutation UpdateEvent($input: EventMutationInput!) {
        updateEvent(input: $input) {
            event {
                id
                name
                soldOut
                cancelled
                waterTemp
            }
        }
    }
    """

    variables = {
        "input": {
            "id": event_id,
            "name": "Updated Test Swimming Event",
            "soldOut": True,
            "waterTemp": 18.5,
        }
    }

    run_mutation(client, update_mutation, variables, "Update Event", context)

    return event_id


def test_race_mutations(client, event_id, context):
    """Test Race create, update, delete mutations"""
    print_header("Testing Race Mutations")

    # 1. Create Race
    create_mutation = """
    mutation CreateRace($input: CreateRaceMutationInput!) {
        createRace(input: $input) {
            race {
                id
                distance
                date
                raceTime
                name
                wetsuit
                priceValue
                priceCurrency
            }
        }
    }
    """

    variables = {
        "input": {
            "eventId": event_id,
            "date": str(date.today()),
            "distance": 5.0,
            "raceTime": "09:00:00",
            "name": "5km Open Water",
            "wetsuit": "optional",
            "priceValue": 45.00,
            "priceCurrency": "CHF",
        }
    }

    result = run_mutation(client, create_mutation, variables, "Create Race", context)
    if not result:
        return None

    race_id = result["createRace"]["race"]["id"]
    print(f"   Created Race ID: {race_id}")

    # 2. Update Race
    update_mutation = """
    mutation UpdateRace($input: RaceMutationInput!) {
        updateRace(input: $input) {
            race {
                id
                distance
                name
                priceValue
                priceCurrency
            }
        }
    }
    """

    variables = {
        "input": {
            "id": race_id,
            "distance": 10.0,
            "name": "10km Open Water",
            "priceValue": 60.00,
        }
    }

    run_mutation(client, update_mutation, variables, "Update Race", context)

    return race_id


def test_delete_mutations(client, race_id, event_id, organizer_id, location_id, context):
    """Test all delete mutations"""
    print_header("Testing Delete Mutations")

    # 1. Delete Race
    delete_race_mutation = """
    mutation DeleteRace($input: DeleteRaceMutationInput!) {
        deleteRace(input: $input) {
            success
            deletedId
        }
    }
    """

    variables = {"input": {"id": race_id}}
    run_mutation(client, delete_race_mutation, variables, "Delete Race", context)

    # 2. Delete Event
    delete_event_mutation = """
    mutation DeleteEvent($input: DeleteEventMutationInput!) {
        deleteEvent(input: $input) {
            success
            deletedId
        }
    }
    """

    variables = {"input": {"id": event_id}}
    run_mutation(client, delete_event_mutation, variables, "Delete Event", context)

    # 3. Delete Organizer
    delete_organizer_mutation = """
    mutation DeleteOrganizer($input: DeleteOrganizerMutationInput!) {
        deleteOrganizer(input: $input) {
            success
            deletedId
        }
    }
    """

    variables = {"input": {"id": organizer_id}}
    run_mutation(
        client, delete_organizer_mutation, variables, "Delete Organizer", context
    )

    # 4. Delete Location
    delete_location_mutation = """
    mutation DeleteLocation($input: DeleteLocationMutationInput!) {
        deleteLocation(input: $input) {
            success
            deletedId
        }
    }
    """

    variables = {"input": {"id": location_id}}
    run_mutation(
        client, delete_location_mutation, variables, "Delete Location", context
    )


def main():
    """Main test execution"""
    print_header("GraphQL Mutation Test Suite")
    print_info("This script will test all newly implemented mutations.")
    print_warning(
        "Note: Test data will be created and then deleted at the end."
    )

    input("\nPress Enter to continue...")

    # Authenticate
    user = authenticate_user()

    # Create mock request context
    context = create_mock_request(user)

    # Create GraphQL client
    client = Client(schema)

    # Test Location mutations
    location_id = test_location_mutations(client, context)
    if not location_id:
        print_error("Location mutations failed. Aborting.")
        return

    # Test Organizer mutations
    organizer_id = test_organizer_mutations(client, context)
    if not organizer_id:
        print_error("Organizer mutations failed. Aborting.")
        return

    # Test Event mutations
    event_id = test_event_mutations(client, location_id, organizer_id, context)
    if not event_id:
        print_error("Event mutations failed. Aborting.")
        return

    # Test Race mutations
    race_id = test_race_mutations(client, event_id, context)
    if not race_id:
        print_error("Race mutations failed. Aborting.")
        return

    # Ask before cleanup
    print_header("Cleanup")
    cleanup = (
        input("Do you want to delete the test data? (y/n): ").lower() == "y"
    )

    if cleanup:
        test_delete_mutations(
            client, race_id, event_id, organizer_id, location_id, context
        )
    else:
        print_warning("Test data was NOT deleted.")
        print_info(f"Race ID: {race_id}")
        print_info(f"Event ID: {event_id}")
        print_info(f"Organizer ID: {organizer_id}")
        print_info(f"Location ID: {location_id}")

    print_header("Test Complete")
    print_success("All mutation tests completed!")


if __name__ == "__main__":
    main()
