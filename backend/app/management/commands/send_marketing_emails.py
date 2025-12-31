import logging
import os
from datetime import date, datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Sum

from app.models import Organizer, Event
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Send marketing emails to organizers showing their events' analytics. "
        "Duplicate prevention: organizers are skipped if already emailed "
        "(tracked via marketing_email_sent_at). Use --force to resend."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            default=date.today().year,
            help="Year to filter events (default: current year)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what would be sent without actually sending",
        )
        parser.add_argument(
            "--test-email",
            type=str,
            help="Send test email to this address instead of organizer's email",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of organizers to process",
        )
        parser.add_argument(
            "--min-users",
            type=int,
            default=1,
            help="Minimum total active users to include (default: 1)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Send even if already sent before",
        )
        parser.add_argument(
            "--organizer-id",
            type=int,
            help="Send to a specific organizer by ID (for testing)",
        )

    def _setup_file_logging(self):
        """Set up file logging to backend/logs/marketing_emails_YYYYMMDD.log"""
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        logs_dir = os.path.join(settings.BASE_DIR, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_file_path = os.path.join(
            logs_dir, f'marketing_emails_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        return log_file_path

    def _log(self, message, style=None):
        """Write to both stdout and log file."""
        if style:
            self.stdout.write(style(message))
        else:
            self.stdout.write(message)
        logger.info(message)

    def handle(self, *args, **options):
        # Set up file logging
        log_file_path = self._setup_file_logging()
        self._log(f"Logging to: {log_file_path}")

        year = options["year"]
        dry_run = options["dry_run"]
        test_email = options.get("test_email")
        limit = options.get("limit")
        min_users = options.get("min_users", 1)
        force = options.get("force", False)
        organizer_id = options.get("organizer_id")

        if dry_run:
            self._log(
                "Running in DRY RUN mode - no emails will be sent",
                self.style.WARNING
            )

        email_service = EmailService()

        # Build organizer query
        if organizer_id:
            organizers = Organizer.objects.filter(id=organizer_id)
        else:
            organizers = Organizer.objects.filter(
                contact_email__isnull=False,
            ).exclude(contact_email="")

            # Filter to organizers with events in the specified year
            organizers = organizers.filter(
                events__date_start__year=year,
            ).distinct()

            # Exclude already-emailed unless force
            if not force:
                organizers = organizers.filter(marketing_email_sent_at__isnull=True)

        # Order by name for consistent output
        organizers = organizers.order_by("name")

        self._log(f"Found {organizers.count()} organizers to process")

        # Apply limit
        if limit:
            organizers = organizers[:limit]
            self._log(f"Limited to {limit} organizers")

        # Process each organizer
        sent_count = 0
        skipped_count = 0
        high_views_count = 0
        low_views_count = 0

        for organizer in organizers:
            self._log(f"\nProcessing: {organizer.name}")

            # Get total active users for this organizer's events
            events_with_stats = organizer.events.filter(
                date_start__year=year,
                active_user_count__isnull=False,
            )
            total_users = (
                events_with_stats.aggregate(total=Sum("active_user_count"))["total"]
                or 0
            )

            # Skip if below minimum
            if total_users < min_users:
                self._log(
                    f"  Skipped: {total_users} users < {min_users} minimum",
                    self.style.WARNING
                )
                skipped_count += 1
                continue

            variant = "high_views" if total_users > 100 else "low_views"
            self._log(f"  Total users: {total_users} ({variant})")
            self._log(f"  Email: {organizer.contact_email}")

            if dry_run:
                self._log("  [DRY RUN] Would send email", self.style.SUCCESS)
                sent_count += 1
                if variant == "high_views":
                    high_views_count += 1
                else:
                    low_views_count += 1
                continue

            # Send the email
            result = email_service.send_marketing_email(
                organizer=organizer,
                year=year,
                test_email=test_email,
                stdout=self.stdout,
            )

            if result["success"]:
                sent_count += 1
                if result["variant"] == "high_views":
                    high_views_count += 1
                else:
                    low_views_count += 1
                self._log(f"  Sent: {result['message']}", self.style.SUCCESS)
            else:
                self._log(f"  Failed: {result['message']}", self.style.ERROR)

        # Summary
        prefix = "[DRY RUN] " if dry_run else ""
        summary = (
            f"\n{prefix}Summary:\n"
            f"- Emails sent: {sent_count}\n"
            f"  - High views (>100 users): {high_views_count}\n"
            f"  - Low views: {low_views_count}\n"
            f"- Skipped (below min users): {skipped_count}\n"
            f"- Total processed: {sent_count + skipped_count}"
        )
        self._log(summary, self.style.SUCCESS)
