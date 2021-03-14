import csv
import json

from django.core.management import BaseCommand
import dateparser
import re


def map_row(row, header: list):
    return {
        v: row[k] for k, v in enumerate(header)
    }


WATER_TYPE_MAP = {
    "Lac": "Lake Swim",
    "Mer": "Sea Swim",
    "Canal": "River Swim",
    "Rivière": "River Swim",
}


class Command(BaseCommand):
    """
    Expected import format:

    Etape,Evenement,Lieu,Date,Lieu,Milieu,Distance,Ligue,Support,Contact,Added \
    1,Guadeloupe - Sainte-Anne,25 Avril,Sainte-Anne - Plage du Bourg (971),Mer,5 km,
    Guadeloupe, Ligue Guadeloupe,ligueng@orange.fr,No
    2,Vitré Nage Ô Naturel,8 Mai,Saint-M'Hervé - Base de Loisirs de Haute-Vilaine
    (35),Lac,5 / 2 km, Bretagne, Club Vitréen de Natation,nono.floflo@hotmail.fr,Yes

    OUTPUT:
    {
      "wetsuit": "Wetsuit Optional",
      "water_type": "Lake Swim",
      "name": "Keswick Mountain Festival Derwent Swims",
      "date_start": "2021-05-22 00:00:00",
      "races": [
        1.5,
        3.0
      ],
      "website": "http://keswickmountainfestival.co.uk",
      "description": "5k Open Water Swim; Derwent Island 1500m Swim; Derwentwater 3km Open Water Swim; keswickmountainfestival.co.uk",
      "location": "Crow Park,Keswick,Cumbria UK",
      "source": "championnat de france"
    },

    """
    help = "Converts a Excel from https://ffn.extranat.fr/html/dossiers/2557.pdf" \
           " to JSON which can be used by scrapy_import command"

    def add_arguments(self, parser):
        parser.add_argument("path", help="Path to the CSV file")

    def handle(self, *args, **options):
        out = []
        with open(options['path'], 'r') as f:
            reader = csv.reader(f)
            header = reader.__next__()
            for in_row_raw in reader:
                in_row = map_row(in_row_raw, header)
                out_row = {}
                out_row['wetsuit'] = "Wetsuit Optional"
                out_row['name'] = in_row['Evenement']

                m = re.match(r'(\d+)(?:-(\d+))? (.*)$', in_row['Date'])
                out_row['date_start'] = dateparser.parse(f"{m.group(1)} {m.group(3)} 2021").strftime(
                    '%Y-%m-%d')
                if m.group(2):
                    out_row['date_end'] = dateparser.parse(f"{m.group(2)} {m.group(3)} 2021").strftime(
                        '%Y-%m-%d')
                else:
                    out_row['date_end'] = out_row['date_start']

                matches = re.findall(r'[\d,]+', in_row['Distance'])
                out_row['races'] = [float(v.replace(',', '.')) for v in matches]

                out_row['location'] = in_row['Lieu'] + ', France'

                out_row['water_type'] = WATER_TYPE_MAP[in_row['Milieu']]

                out.append(out_row)

        self.stdout.write(json.dumps(out, indent=True))

        # self.stdout.write(f"Updating {r.distance}")
