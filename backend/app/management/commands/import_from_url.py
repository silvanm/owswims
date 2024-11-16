from click import BaseCommand


class Command(BaseCommand):
    help = "Imports a GPX to a race"

    def add_arguments(self, parser):
        parser.add_argument("url", help="Path to the kml file")
        parser.add_argument("race_id", help="Id of the race to add the route to")

    def handle(self, *args, **options):