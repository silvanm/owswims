from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from app.models import Organizer, Event
from app.services.organizer_contact_service import OrganizerContactService
import logging
from django.db.models import Q

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
    Uses AI to find contact information for organizers of future events that lack contact details.
    
    This command:
    1. Identifies all organizers that have events with start dates in the future
    2. Filters to only process organizers WITHOUT existing contact information
       (those with no email address and no contact form URL)
    3. Attempts to find contact information (email, contact form URLs) using AI services
    
    By default, the command only processes organizers without contact information.
    Use the --all flag to process all organizers regardless of their current contact status.
    
    Results are categorized as:
    - Success: Contact information found with high confidence
    - Needs review: Contact information found but with lower confidence
    - Failed: No contact information could be found
    
    You can specify a particular organizer to process using the --organizer option.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset existing contact information before processing",
        )
        parser.add_argument(
            "--organizer", type=str, help="Process only a specific organizer by name"
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all organizers including those with existing contact information",
        )

    def handle(self, *args, **options):
        # Get organizers of future events
        future_events = Event.objects.filter(date_start__gte=timezone.now())
        organizers = Organizer.objects.filter(events__in=future_events).distinct()

        # Filter out organizers that already have contact information unless --all is specified
        if not options["all"]:
            organizers = organizers.filter(
                Q(contact_email__isnull=True) | Q(contact_email=""),
                Q(contact_form_url__isnull=True) | Q(contact_form_url=""),
            )
            self.stdout.write(
                "Filtering to process only organizers without contact information"
            )

        # Filter for specific organizer if requested
        if options["organizer"]:
            organizers = organizers.filter(name__icontains=options["organizer"])
            if not organizers.exists():
                self.stdout.write(
                    self.style.ERROR(
                        f"No organizer found matching: {options['organizer']}"
                    )
                )
                return

        total_organizers = organizers.count()
        self.stdout.write(f"Found {total_organizers} organizers to process")

        # Initialize the service
        service = OrganizerContactService(firecrawl_api_key=settings.FIRECRAWL_API_KEY)

        if options["reset"]:
            organizers.update(
                contact_email=None,
                contact_form_url=None,
                contact_status="pending",
                contact_notes="",
            )
            self.stdout.write("Reset existing contact information")

        results = {"success": 0, "failed": 0, "needs_review": 0}

        # Process each organizer
        for i, organizer in enumerate(organizers, 1):
            self.stdout.write(
                f"\nProcessing organizer {i}/{total_organizers}: {organizer.name}..."
            )

            result = service.process_organizer(organizer)

            if result:
                status = (
                    "needs_review" if result["confidence_score"] < 0.8 else "success"
                )
                results[status] += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found contact info for {organizer.name}\n"
                        f"Primary method: {result['primary_contact_method']}\n"
                        f"Source: {result['source_type']} ({result['source_url']})\n"
                        f"Confidence: {result['confidence_score']:.2f}\n"
                        f"Registration specific: {result['registration_specific']}\n"
                        f"Notes: {result['contact_notes']}"
                    )
                )
            else:
                results["failed"] += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Failed to find contact info for {organizer.name}"
                    )
                )

        # Print summary
        self.stdout.write("\nSummary:")
        self.stdout.write(f"Successfully processed: {results['success']}")
        self.stdout.write(f"Needs review: {results['needs_review']}")
        self.stdout.write(f"Failed: {results['failed']}")
        self.stdout.write(f"Total organizers processed: {total_organizers}")
