import logging
from typing import Optional, Dict, Any
from django.conf import settings
from django.utils import timezone
from sparkpost import SparkPost
from app.models import Organizer, Event
from app.services.llm_service import LLMService
from pydantic import BaseModel, Field

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


class EmailService:
    def __init__(self):
        self.sparkpost = SparkPost(settings.SPARKPOST_API_KEY)
        self.llm_service = LLMService()

    def generate_email_content(
        self, organizer: Organizer, prompt_extension: Optional[str] = None
    ) -> EmailGenerationResult:
        """Generate email content using GPT-4 based on organizer's events, including a data quality check."""
        events = organizer.events.filter(date_start__gte=timezone.now())

        language = "en"  # default to English
        first_event_location_info = "N/A"
        if events.exists():
            first_event = events.first()
            if first_event.location:
                # Let GPT-4 determine the language based on country/city
                language_prompt = f"""

                Determine the language that the organizer {organizer.name} (website: {organizer.website}) probably speaks.

                If the name of the organizer does not contain any language information or the website is empty, 
                use the language of the first event: Based on the location {first_event.location.city}, {first_event.location.country.name},

                Return only the ISO language code (e.g., 'en', 'de', 'fr', 'it').
                """
                language = (
                    self.llm_service.get_completion(language_prompt).strip().lower()
                )
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
