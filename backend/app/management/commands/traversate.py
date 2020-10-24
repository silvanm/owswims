from django.core.management.base import BaseCommand
from app.services import import_events


class Command(BaseCommand):

    def handle(self, *args, **options):
        import_events()
