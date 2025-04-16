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


class EmailService:
    def __init__(self):
        self.sparkpost = SparkPost(settings.SPARKPOST_API_KEY)
        self.llm_service = LLMService()

    def generate_email_content(self, organizer: Organizer) -> Dict[str, str]:
        """Generate email content using GPT-4 based on organizer's events"""
        events = organizer.events.filter(date_start__gte=timezone.now())

        # Get the primary language based on the first event's location
        language = "en"  # default to English
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

        # Prepare event information
        event_info = []
        for event in events:
            event_url = f"https://open-water-swims.com/event/{event.slug}"
            event_info.append(f"- {event.name} ({event.date_start}): {event_url}")

        # Generate email content
        prompt = f"""
        Write an informal email in language code "{language}" to inform the organizer {organizer.name} that their single event (or their multiple events)
        have been added to our website. The site is called "open-water-swims.com" and the URL is https://open-water-swims.com.
        The email should be friendly and helpful, mentioning that we've added their events to help swimmers discover them. 

        The email should not be too formal. It is communication among swimmers and event organizers. Don't be too salesy or excited.

        It should also ask the organizer to report any issues or missing events.

        The events should be included as a bullet list if there is more than one event. Otherwise, just mention the event without bullet. Always make the event name a link to the event page.

        The dates should correspond to the locales in the country: {first_event.location.country.name}.
        
        Events added:
        {chr(10).join(event_info)}
        
        Guidelines:
        - Keep it professional but friendly
        - Don't be too salesy
        - Mention that swimmers can find their events on our platform
        - Include the event links
        - Keep it concise (max 3 paragraphs)
        - The mail should be signed with 'Silvan Mühlemann'
        - If there is only one event use the singular form in subject and body.
        - If there is more than one event use the plural form in subject and body.
        - Create a short but personalized subject line for the email
        """

        system_prompt = "You are a helpful assistant that generates professional email content with both subject and body."

        try:
            email_data = self.llm_service.parse_completion(
                prompt=prompt, response_model=EmailContent, system_prompt=system_prompt
            )

            return {"subject": email_data.subject, "body": email_data.body}
        except Exception as e:
            logger.error(f"Error parsing email content: {str(e)}")
            # Fallback to the old method if parsing fails
            response = self.llm_service.get_completion(prompt)
            try:
                import json

                email_data = json.loads(response)
                return email_data
            except json.JSONDecodeError:
                logger.error(
                    f"Failed to parse LLM response as JSON: {response[:100]}..."
                )
                # Final fallback - return the response as body with a default subject
                return {"subject": f"Your events on Open Water Swims", "body": response}

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
