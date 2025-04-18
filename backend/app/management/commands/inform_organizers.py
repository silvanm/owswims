import argparse
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from app.models import Organizer
from app.services.email_service import EmailService
import html2text  # Assume it's always available


class Command(BaseCommand):
    help = "Sends informational emails to organizers with pending contact status and future events."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the process without sending emails or updating the database.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of organizers to process.",
        )
        parser.add_argument(
            "--prompt-extension",
            type=str,
            default=None,
            help="Additional text to append to the email generation prompt for customization.",
        )
        parser.add_argument(
            "--interactive",
            action="store_true",
            help="Display each email and ask for confirmation before sending.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        limit = options["limit"]
        prompt_extension = options["prompt_extension"]
        interactive = options["interactive"]

        self.stdout.write(self.style.NOTICE("Starting inform_organizers command..."))
        if dry_run:
            self.stdout.write(self.style.WARNING("Running in DRY RUN mode."))

        email_service = EmailService()

        # Query for target organizers
        organizers_qs = (
            Organizer.objects.filter(
                contact_status="pending", events__date_start__gte=timezone.now()
            )
            .exclude(contact_email__isnull=True)
            .exclude(contact_email="")
            .distinct()
            .order_by("name")
        )

        total_organizers_found = organizers_qs.count()
        self.stdout.write(
            f"Found {total_organizers_found} potential organizers to process."
        )

        if limit:
            organizers_qs = organizers_qs[:limit]
            self.stdout.write(
                f"Processing a maximum of {limit} organizers due to --limit."
            )

        processed_count = 0
        sent_count = 0
        current_organizer_index = 0

        for organizer in organizers_qs:
            current_organizer_index += 1
            processed_count += 1
            self.stdout.write(
                f"\n--- Processing {current_organizer_index}/{total_organizers_found}: {organizer.name} ({organizer.contact_email}) ---"
            )

            try:
                while True:  # Loop for regeneration
                    # Generate email content (includes quality check)
                    self.stdout.write(
                        "Generating email content and checking quality..."
                    )
                    generation_result = email_service.generate_email_content(
                        organizer, prompt_extension=prompt_extension
                    )
                    subject = generation_result.subject
                    content_html = generation_result.body
                    quality_warnings = generation_result.quality_warnings

                    # Display Quality Warnings if any
                    if quality_warnings:
                        self.stdout.write(
                            self.style.WARNING("\n--- Data Quality Warnings --- ")
                        )
                        for warning in quality_warnings:
                            self.stdout.write(self.style.WARNING(f"- {warning}"))
                        self.stdout.write(self.style.WARNING("--- End Warnings ---"))

                    if interactive:
                        self.stdout.write(self.style.NOTICE("\n--- Email Preview ---"))
                        self.stdout.write(f"To: {organizer.contact_email}")
                        self.stdout.write(f"Subject: {subject}")

                        # Convert HTML to readable text for terminal
                        h = html2text.HTML2Text()
                        # h.ignore_links = True # Optional: configure as needed
                        content_text = h.handle(content_html)
                        self.stdout.write(f"Body (converted to text):\n{content_text}")

                        self.stdout.write(self.style.NOTICE("--- End Preview ---"))

                        confirm = input(
                            "Send? (y/N/s/r) (s=skip & review, r=regenerate): "
                        ).lower()

                        if confirm == "r":
                            self.stdout.write(
                                self.style.WARNING("Regenerating email content...")
                            )
                            # Optionally, you could ask for a new prompt_extension here
                            # prompt_extension = input("Enter new prompt extension (or leave blank): ")
                            continue  # Re-run the generation in the while loop

                        # If not regenerating, break out of the inner loop to proceed
                        break
                    else:
                        # If not interactive, generate once and break the inner loop
                        confirm = "y"  # Assume 'yes' if not interactive
                        break
                # --- End of regeneration loop ---

                # Handle the final user decision (confirm will hold 'y', 's', or 'n'/default)
                if confirm == "s":
                    self.stdout.write(
                        self.style.WARNING("Skipping and marking for review.")
                    )
                    if not dry_run:
                        organizer.contact_status = "needs_review"
                        organizer.last_contact_attempt = timezone.now()
                        # Add a note about skipping
                        timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                        skip_note = (
                            f"Skipped via inform_organizers script on {timestamp}."
                        )
                        if organizer.contact_notes:
                            organizer.contact_notes += f"\n\n{skip_note}"
                        else:
                            organizer.contact_notes = skip_note
                        organizer.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Marked {organizer.name} as needs_review."
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"DRY RUN: Would mark {organizer.name} as needs_review."
                            )
                        )
                    continue  # Skip to the next organizer in the outer loop

                elif confirm != "y":
                    self.stdout.write(
                        self.style.WARNING("Skipping email send based on user input.")
                    )
                    continue  # Skip to the next organizer in the outer loop

                # --- If confirm == 'y', proceed with sending ---

                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(
                            f"DRY RUN: Would send email with subject '{subject}' to {organizer.contact_email}"
                        )
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f"DRY RUN: Would update {organizer.name} status to 'contacted'"
                        )
                    )
                    continue  # Skip actual sending/saving

                # Send email
                self.stdout.write(f"Sending email to {organizer.contact_email}...")
                success = email_service.send_email(
                    organizer=organizer,
                    subject=subject,
                    content=content_html,  # Send the original HTML content
                    # Use the organizer's email directly, send_email handles the update logic now
                )

                if success:
                    sent_count += 1
                    # Note: Organizer status/notes update is handled within send_email now
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Email sent successfully to {organizer.name} and status updated."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to send email to {organizer.name}.")
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"An error occurred processing {organizer.name}: {e}"
                    )
                )
                # Decide if you want to continue or stop on error
                # continue

        self.stdout.write(self.style.NOTICE(f"\n--- Command Finished ---"))
        self.stdout.write(
            f"Attempted Processing: {processed_count} of {total_organizers_found} organizers found."
        )
        if limit is not None:
            self.stdout.write(f"(Limited to {limit} by --limit flag)")
        if not dry_run:
            self.stdout.write(f"Emails Sent: {sent_count}.")
        self.stdout.write(self.style.SUCCESS("inform_organizers command completed."))
