from django.core.management.base import BaseCommand
from django.utils.text import slugify
from app.models import Organizer


class Command(BaseCommand):
    help = "Populates the slug field for all organizers that don't have one"

    def handle(self, *args, **options):
        organizers = Organizer.objects.filter(slug__isnull=True)

        # Pre-fetch all existing slugs to avoid N+1 queries
        existing_slugs = set(
            Organizer.objects.exclude(slug__isnull=True).values_list('slug', flat=True)
        )
        count = 0

        for organizer in organizers:
            # Generate a slug from the name
            base_slug = slugify(organizer.name)
            slug = base_slug
            counter = 1

            # Check against cached set instead of database
            while slug in existing_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1

            organizer.slug = slug
            existing_slugs.add(slug)  # Add to set to avoid duplicates in this run
            organizer.save()
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully populated slugs for {count} organizers")
        )
