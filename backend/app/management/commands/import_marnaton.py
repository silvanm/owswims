import os
import re

from django.core.management import BaseCommand
from app.models import Race


class Command(BaseCommand):
    def handle(self, *args, **options):
        dirname = '/Users/silvan.muehlemann/PycharmProjects/owswims/tmp'
        for filename in os.listdir(dirname):
            g = re.match(r'(\d{4}).csv', filename)
            if g:
                out = []
                id = g.group(1)
                race = Race.objects.get(pk=id)
                self.stdout.write(f"Updating {id} ({race.name})")
                with open(os.path.join(dirname, filename), 'r') as r:
                    lines = r.readlines()
                    for line in lines:
                        #print(line)
                        l = re.search(r'([\d\.]*),([\d\.]*),([\d\.]*)', line)
                        if l:
                            out.append([l.group(2), l.group(1)])
                    #print(out)
                race.coordinates = out
                race.save()
