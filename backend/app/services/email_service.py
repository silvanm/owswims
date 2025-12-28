import json
import logging
import os
from datetime import date
from typing import Optional, Dict, Any, List

from django.conf import settings
from django.utils import timezone
from pydantic import BaseModel, Field
from sparkpost import SparkPost

from app.models import Organizer, Event, EventSubmission
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class EmailContent(BaseModel):
    subject: str = Field(description="A short personalized subject line for the email")
    body: str = Field(
        description="The HTML content of the email body without any markdown formatting"
    )


# New model to include quality checks
class EmailGenerationResult(BaseModel):
    quality_warnings: list[str] = Field(
        default_factory=list,
        description="A list of potential data quality issues found (e.g., duplicate events, location mismatches).",
    )
    subject: str = Field(description="A short personalized subject line for the email")
    body: str = Field(
        description="The HTML content of the email body without any markdown formatting"
    )


class TranslatedTemplate(BaseModel):
    subject: str = Field(description="The translated email subject line")
    body: str = Field(description="The translated email body in HTML format")


class EmailService:
    def __init__(self):
        self.sparkpost = SparkPost(settings.SPARKPOST_API_KEY)
        self.llm_service = LLMService()

    def generate_email_content(
        self, organizer: Organizer, prompt_extension: Optional[str] = None
    ) -> EmailGenerationResult:
        """Generate email content using GPT-4 based on organizer's events, including a data quality check."""
        events = organizer.events.filter(date_start__gte=timezone.now())

        # Get or detect language (uses cached value if available)
        language = self.get_or_detect_language(organizer)

        first_event_location_info = "N/A"
        if events.exists():
            first_event = events.first()
            if first_event.location:
                first_event_location_info = (
                    f"{first_event.location.city}, {first_event.location.country.name}"
                )

        # Prepare event information string for the prompt
        event_strings_for_prompt = []
        for event in events:
            event_url = f"https://open-water-swims.com/event/{event.slug}"
            event_strings_for_prompt.append(
                f"- Name: {event.name}, Date: {event.date_start}, Slug: {event.slug}, URL: {event_url}"
            )
        event_info_str = "\n".join(event_strings_for_prompt)

        # Generate email content
        prompt = f"""
        Phase 1: Data Quality Check
        Carefully review the following event data provided for organizer {organizer.name}. The primary location context is {first_event_location_info}.
        Event List:
        {event_info_str}
        
        Perform these checks:
        1. Duplicate Events: Check if any events in the list appear to be duplicates based on name and date.
        2. Location Consistency: Check if the provided location context ('{first_event_location_info}') seems plausible/consistent. For example, is the city actually in the country mentioned?
        
        List any potential issues found as strings in the 'quality_warnings' field. Provide the findings **in English**. If no issues are found, provide an empty list [].
        
        Phase 2: Email Generation
        After performing the quality checks, write an informal email in language code "{language}" to inform the organizer {organizer.name} that their event(s) have been added to our website (open-water-swims.com, URL https://open-water-swims.com).
        Mention the site helps swimmers discover their events. Ask them to report issues or missing events.
        
        Guidelines for email:
        - Use the event list provided above. Include links ({event_url}). Format as a bullet list if multiple events.
        - Use date formats appropriate for {first_event_location_info}.
        - Keep it friendly, not too formal or salesy. And not too enthusiastic.
        - be aware that in Switzerland we don't use the letter "ß" and we use "ss" instead.
        - In Switzerland, use a informal tone.
        - If the organiser is a organisation, use the plural form.
        - Sign off with 'Silvan Mühlemann'. 
        - Use singular/plural forms appropriately based on event count.
        - Generate a short, personalized subject line.
        - Max 3 paragraphs.

        Give an explanation about what open-water-swims.com: It is a not-for-profit project from 
        open-water swimmers for open-water swimmers. We want to help swimmers find the perfect swim events.
        """

        if prompt_extension:
            prompt += (
                f"\n\nAdditional instructions for email generation: {prompt_extension}"
            )

        system_prompt = f"You are a helpful assistant. First, perform data quality checks and report findings **in English** in 'quality_warnings'. Second, generate professional email content ('subject', 'body') in the requested language based on the guidelines. Respond strictly in the required JSON format matching the EmailGenerationResult model."

        try:
            email_result = self.llm_service.parse_completion(
                prompt=prompt,
                response_model=EmailGenerationResult,
                system_prompt=system_prompt,
            )
            return email_result
        except Exception as e:
            logger.error(f"Error parsing email generation result: {str(e)}")
            # Fallback: Return an object with error indication
            return EmailGenerationResult(
                quality_warnings=[f"Error during generation: {str(e)}"],
                subject="Error Generating Email",
                body="Could not generate email content due to an error.",
            )

    def send_email(
        self, organizer: Organizer, subject: str, content: str, to_email: str = None
    ) -> bool:
        """Send email using SparkPost"""
        try:
            recipient_email = to_email or organizer.contact_email

            response = self.sparkpost.transmissions.send(
                recipients=[recipient_email],
                cc=["silvan@open-water-swims.com"],
                template="owswims-default",
                subject=subject,
                substitution_data={"email_content": content, "subject": subject},
            )

            # Update organizer status
            organizer.contact_status = "contacted"
            organizer.last_contact_attempt = timezone.now()
            organizer.contact_notes = f"{organizer.contact_notes}\n\nEmail sent on {timezone.now()}: {subject}"
            organizer.save()

            logger.info(f"Email sent successfully to {organizer.name}: {response}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {organizer.name}: {str(e)}")
            return False

    def send_submission_notification(self, submission: EventSubmission) -> bool:
        """Send notification email when a new event URL is submitted"""
        try:
            admin_email = "silvan@open-water-swims.com"
            subject = f"New Event Submission: {submission.url}"

            content = f"""
            <p>A new event URL has been submitted:</p>
            <ul>
                <li><strong>URL:</strong> <a href="{submission.url}">{submission.url}</a></li>
                <li><strong>Email:</strong> {submission.email or 'Not provided'}</li>
                <li><strong>Comment:</strong> {submission.comment or 'None'}</li>
                <li><strong>Submitted at:</strong> {submission.created_at}</li>
            </ul>
            <p><a href="https://open-water-swims.com/admin/app/eventsubmission/{submission.id}/change/">View in Admin</a></p>
            """

            response = self.sparkpost.transmissions.send(
                recipients=[admin_email],
                template="owswims-default",
                subject=subject,
                substitution_data={"email_content": content, "subject": subject},
            )

            logger.info(f"Submission notification sent: {response}")
            return True

        except Exception as e:
            logger.error(f"Failed to send submission notification: {str(e)}")
            return False

    def _load_marketing_templates(self) -> Dict:
        """Load marketing email templates from JSON file."""
        template_path = os.path.join(
            settings.BASE_DIR, "app", "data", "marketing_email_templates.json"
        )
        with open(template_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_marketing_templates(self, templates: Dict) -> None:
        """Save marketing email templates to JSON file."""
        template_path = os.path.join(
            settings.BASE_DIR, "app", "data", "marketing_email_templates.json"
        )
        with open(template_path, "w", encoding="utf-8") as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)

    def detect_language(self, organizer: Organizer) -> str:
        """Detect the language for an organizer based on their location."""
        # Try to get language from first event's location
        events = organizer.events.all()
        first_event_with_location = None

        for event in events:
            if event.location:
                first_event_with_location = event
                break

        if not first_event_with_location or not first_event_with_location.location:
            return "en"

        location = first_event_with_location.location
        location_info = f"{location.city}, {location.country.name}"

        language_prompt = f"""
        Determine the language that the organizer {organizer.name} (website: {organizer.website}) probably speaks.

        If the name of the organizer does not contain any language information or the website is empty,
        use the language of the location: {location_info}

        Return only the ISO language code (e.g., 'en', 'de', 'fr', 'it', 'es').
        """
        try:
            language = self.llm_service.get_completion(language_prompt).strip().lower()
            # Validate it's a reasonable language code
            if len(language) == 2 and language.isalpha():
                return language
            return "en"
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "en"

    def get_or_detect_language(self, organizer: Organizer) -> str:
        """
        Get the organizer's language, detecting and saving it if not already set.

        Args:
            organizer: The organizer to get language for

        Returns:
            ISO language code (e.g., 'en', 'de', 'fr')
        """
        if organizer.language:
            return organizer.language

        # Detect language and save it
        language = self.detect_language(organizer)
        organizer.language = language
        organizer.save(update_fields=["language"])
        logger.info(f"Detected and saved language '{language}' for organizer {organizer.name}")
        return language

    def get_translated_template(self, variant: str, language: str) -> Dict[str, str]:
        """
        Get translated template for the given variant and language.
        If translation doesn't exist, generate it via LLM and cache it.

        Args:
            variant: 'high_views' or 'low_views'
            language: ISO language code (e.g., 'en', 'de', 'fr')

        Returns:
            Dict with 'subject' and 'body' keys
        """
        templates = self._load_marketing_templates()

        # Check if translation exists
        if variant in templates and language in templates[variant]:
            return templates[variant][language]

        # Generate translation from English template
        english_template = templates[variant]["en"]

        if language == "en":
            return english_template

        translate_prompt = f"""
        Translate the following email template from English to {language}.
        Keep the HTML formatting intact. Keep all placeholders like {{organizer_name}}, {{total_users}},
        {{event_table}}, {{total_event_count}} exactly as they are - do not translate them.

        Subject: {english_template['subject']}

        Body:
        {english_template['body']}

        Return the translated subject and body.
        """

        try:
            result = self.llm_service.parse_completion(
                prompt=translate_prompt,
                response_model=TranslatedTemplate,
                system_prompt="You are a professional translator. Translate the email template accurately while preserving HTML formatting and placeholders.",
            )

            # Cache the translation
            if variant not in templates:
                templates[variant] = {}
            templates[variant][language] = {
                "subject": result.subject,
                "body": result.body,
            }
            self._save_marketing_templates(templates)

            return templates[variant][language]

        except Exception as e:
            logger.error(f"Error translating template to {language}: {e}")
            # Fall back to English
            return english_template

    def send_marketing_email(
        self,
        organizer: Organizer,
        year: int = None,
        test_email: str = None,
        stdout=None,
    ) -> Dict[str, Any]:
        """
        Send marketing email to an organizer showing their events' analytics.

        Args:
            organizer: The organizer to send email to
            year: Year to filter events (default: current year)
            test_email: If provided, send to this email instead and don't update tracking
            stdout: Optional stream for logging output

        Returns:
            Dict with 'success', 'message', 'variant', 'total_users' keys
        """
        if year is None:
            year = date.today().year

        def log(msg):
            if stdout:
                stdout.write(msg + "\n")
            logger.info(msg)

        # Get organizer's events for the specified year
        events = organizer.events.filter(
            date_start__year=year,
            active_user_count__isnull=False,
        ).order_by("-active_user_count")

        # Calculate total active users
        total_users = sum(e.active_user_count or 0 for e in events)

        # Determine which template variant to use
        variant = "high_views" if total_users > 100 else "low_views"

        # Get or detect language
        language = self.get_or_detect_language(organizer)
        log(f"  Language: {language}")

        # Get translated template
        template = self.get_translated_template(variant, language)

        # Prepare substitution data
        organizer_name = organizer.name

        # Get all events for this organizer in the year (for low_views we show all, not just those with stats)
        all_events = organizer.events.filter(
            date_start__year=year,
        ).order_by("date_start")

        # Build event table HTML
        event_table_html = ""
        if variant == "high_views" and events:
            # High views: show table with "Interested Swimmers" column
            event_table_html = """
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <tr style="background-color: #f2f2f2;">
    <th style="text-align: left;">Event</th>
    <th style="text-align: left;">Date</th>
    <th style="text-align: right;">Interested Swimmers</th>
  </tr>
"""
            for event in events:
                event_date = event.date_start.strftime("%d.%m.%Y") if event.date_start else "TBD"
                event_table_html += f"""  <tr>
    <td>{event.name}</td>
    <td>{event_date}</td>
    <td style="text-align: right;">{event.active_user_count or 0}</td>
  </tr>
"""
            event_table_html += "</table>"
        elif variant == "low_views" and all_events:
            # Low views: show simple table without stats column
            event_table_html = """
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%;">
  <tr style="background-color: #f2f2f2;">
    <th style="text-align: left;">Event</th>
    <th style="text-align: left;">Date</th>
  </tr>
"""
            for event in all_events:
                event_date = event.date_start.strftime("%d.%m.%Y") if event.date_start else "TBD"
                event_table_html += f"""  <tr>
    <td>{event.name}</td>
    <td>{event_date}</td>
  </tr>
"""
            event_table_html += "</table>"

        # Get total event count for low-views variant
        total_event_count = Event.objects.filter(date_start__year=year).count()

        # Check for next year events (e.g., 2026) - only visible ones
        next_year = year + 1
        next_year_events = organizer.events.filter(
            date_start__year=next_year,
            invisible=False,
        ).order_by("date_start")

        next_year_events_html = ""
        if next_year_events.exists():
            log(f"  {next_year} events: {next_year_events.count()}")
            next_year_events_html = f"<p>Great news! Your {next_year} events are already published on our platform:</p>\n<ul>\n"
            for event in next_year_events:
                event_url = f"https://open-water-swims.com/event/{event.slug}"
                event_date = event.date_start.strftime("%d.%m.%Y") if event.date_start else "TBD"
                next_year_events_html += f'  <li><a href="{event_url}">{event.name}</a> ({event_date})</li>\n'
            next_year_events_html += "</ul>\n<p>Please check that all information is correct.</p>\n\n"

        # Fill in template placeholders
        subject = template["subject"].format(
            organizer_name=organizer_name,
            total_users=total_users,
            total_event_count=total_event_count,
        )
        body = template["body"].format(
            organizer_name=organizer_name,
            total_users=total_users,
            event_table=event_table_html,
            total_event_count=total_event_count,
            next_year_events=next_year_events_html,
        )

        # Determine recipient
        recipient = test_email or organizer.contact_email

        if not recipient:
            return {
                "success": False,
                "message": "No email address available",
                "variant": variant,
                "total_users": total_users,
            }

        try:
            response = self.sparkpost.transmissions.send(
                recipients=[recipient],
                cc=["silvan@open-water-swims.com"] if not test_email else [],
                template="owswims-default",
                subject=subject,
                substitution_data={"email_content": body, "subject": subject},
            )

            # Update tracking field (only if not a test email)
            if not test_email:
                organizer.marketing_email_sent_at = timezone.now()
                organizer.save(update_fields=["marketing_email_sent_at"])

            log(f"  Email sent successfully to {recipient}")

            return {
                "success": True,
                "message": f"Email sent to {recipient}",
                "variant": variant,
                "total_users": total_users,
                "language": language,
            }

        except Exception as e:
            logger.error(f"Failed to send marketing email to {organizer.name}: {e}")
            return {
                "success": False,
                "message": str(e),
                "variant": variant,
                "total_users": total_users,
            }
