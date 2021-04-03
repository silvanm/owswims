import json
import os
import pickle

from django.core.management import BaseCommand
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

CACHE_FILE = 'spain_cache.pickle'


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        races = self.get_races()
        self.stdout.write(json.dumps(self.print_as_json(races)))

    def get_races(self):
        # caches it locally
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'rb') as f:
                result = pickle.load(f)
                self.stdout.write(f"Read {len(result['allRaces'])} from {CACHE_FILE}")
        else:
            transport = RequestsHTTPTransport(url="https://api3.calendarioaguasabiertas.com/admin/api",
                                              headers={
                                                  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.51 Safari/537.36'})

            # Create a GraphQL client using the defined transport
            client = Client(transport=transport, fetch_schema_from_transport=True)

            # Provide a GraphQL query
            query = gql(
                """
                    query ALL_RACES_QUERY($published: Boolean, $provincia: RaceProvinciumType, $comunidad: RaceComunidadType, $solidarias: Boolean, $nocturnas: Boolean, $past: Boolean, $startDate: String, $endDate: String, $aviso: String) {
                      allRaces(
                        where: {AND: [{published: $published}, {provincia: $provincia}, {comunidad: $comunidad}, {solidarias: $solidarias}, {nocturnas: $nocturnas}, {past: $past}, {AND: [{date_gte: $startDate}, {date_lt: $endDate}]}, {aviso: $aviso}]}
                      ) {
                        id
                        slug
                        name
                        date
                        website
                        localidad
                        provincia
                        location
                        country
                        lat
                        lng
                        description
                        distances
                        locationV3 {
                          lat
                          lng
                          __typename
                        }
                        __typename
                      }
                    }
                    """
            )
            vars = {
                "past": False,
                "published": True,
                "sortBy": "date_ASC"
            }

            # Execute the query on the transport
            result = client.execute(query, vars)
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(result, f)
                self.stdout.write(f"wrote {len(result['allRaces'])} races to {CACHE_FILE}")

        return result['allRaces']

    def print_as_json(self, races:dict)->list:
        """
        Outputs races in the following format:

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
              "lat": 23.34,
              "lng": 8.32
              "source": "championnat de france"
            },

        :param races:
        :return:
        """

        out = []
        for race in races:
            out_row = {}
            out_row['name'] = race['name']
            out_row['date_start'] = race['date'] + ' 00:00:00'
            out_races = []
            for distance in json.loads(race['distances']):
                out_race = {
                    'km': distance['metros'] / 1000,
                    'price': distance['price'] / 100 if distance['price'] else None
                }
                out_races.append(out_race)
            out_row['races'] = out_races
            if 'website' in race:
                out_row['website'] = race['website']
            if 'description' in race:
                out_row['description'] = race['description']
            if 'localidad' in race:
                out_row['location'] = ", ".join([ race['localidad'], race['provincia'], race['country'] ])
            if 'locationV3' in race and race['locationV3'] is not None:
                out_row['lat'] = race['locationV3']['lat']
                out_row['lng'] = race['locationV3']['lng']
            elif 'lat' in race:
                out_row['lat'] = race['lat']
                out_row['lng'] = race['lng']
            out_row['source'] = 'calendarioaguasabiertas.com'
            out.append(out_row)
        return out
