from pykml import parser
from django.core.management import BaseCommand
from app.models import Race


class Command(BaseCommand):
    help = "Imports a GPX to a race"

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to the kml file")
        parser.add_argument("race_id", help="Id of the race to add the route to")

    def handle(self, *args, **options):
        with open(options['path'], 'r') as f:
            parser.parse(f)
        out = []

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    out.append([point.latitude, point.longitude])

        r = Race.objects.get(pk=options['race_id'])

        self.stdout.write(f"Updating {r.distance}")

        r.coordinates = out
        r.save()
