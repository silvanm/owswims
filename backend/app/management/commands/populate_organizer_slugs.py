from django.core.management.base import BaseCommand
from django.utils.text import slugify
from app.models import Organizer


class Command(BaseCommand):
    help = "Populates the slug field for all organizers that don't have one"

    def handle(self, *args, **options):
        organizers = Organizer.objects.filter(slug__isnull=True)
        count = 0

        for organizer in organizers:
            # Generate a slug from the name
            base_slug = slugify(organizer.name)
            slug = base_slug
            counter = 1

            # Check if slug already exists and append a number if it does
            while Organizer.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            organizer.slug = slug
            organizer.save()
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully populated slugs for {count} organizers")
        )
