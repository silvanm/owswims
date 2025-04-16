import logging
import re
import json
from typing import Optional, Dict, Any, List
from django.conf import settings
from django.utils import timezone
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool

from .scraping_service import ScrapingService
from app.models import Organizer, Event

logger = logging.getLogger(__name__)


class OrganizerContactService:
    """
    Service to intelligently gather contact information for organizers.
    Uses ReActAgent to navigate websites and find contact information.
    """

    def __init__(self, firecrawl_api_key: str):
        self.scraping_service = ScrapingService(api_key=firecrawl_api_key)
        self.llm = OpenAI(model=settings.OPENAI_MODEL)

    def get_organizer_urls(self, organizer: Organizer) -> List[Dict[str, Any]]:
        """Get all relevant URLs for an organizer, including their events"""
        urls = []

        # Get future events for this organizer
        future_events = Event.objects.filter(
            organizer=organizer, date_start__gte=timezone.now()
        )

        # Add organizer website if available
        if organizer.website:
            urls.append({"url": organizer.website, "type": "organizer_website"})

        # Add event websites
        for event in future_events:
            if event.website:
                urls.append(
                    {
                        "url": event.website,
                        "type": "event_website",
                        "event_name": event.name,
                        "event_date": event.date_start,
                    }
                )

        return urls

    def process_organizer(self, organizer: Organizer) -> Optional[Dict[str, Any]]:
        """Process an organizer and their events to find contact information"""
        urls = self.get_organizer_urls(organizer)

        if not urls:
            logger.warning(f"No websites available for organizer: {organizer.name}")
            return None

        logger.info(f"Processing organizer: {organizer.name} with {len(urls)} URLs")

        # Create tools for the LLM
        scrape_tool = FunctionTool.from_defaults(fn=self.scraping_service.scrape)
        agent = ReActAgent.from_tools(
            [scrape_tool], max_iterations=20, llm=self.llm, verbose=True
        )

        # Create the prompt for contact information extraction
        urls_description = "\n".join(
            [
                f"- {url_info['url']} ({url_info['type']}"
                + (
                    f" for event: {url_info['event_name']} on {url_info['event_date']}"
                    if url_info["type"] == "event_website"
                    else ""
                )
                + ")"
                for url_info in urls
            ]
        )

        prompt = f"""You are an expert at finding contact information for swim event organizers. 
        
        Here are the websites related to the organizer "{organizer.name}":
        {urls_description}

        Your task is to find the best way to contact the organizer about their events. You can use the scrape tool to visit any of these URLs or follow links from them.
        
        Look for:
        1. Contact information specifically for event organization/registration
        2. General contact information if event-specific contacts aren't found
        3. Contact forms or registration forms
        4. Social media profiles that allow direct messaging
        5. Phone numbers (as a last resort)

        Important guidelines:
        - Prioritize contact methods specifically mentioned for event registration/organization
        - Look for "Contact", "About", "Impressum", "Kontakt", "Anmeldung", or "Registration" pages
        - Check event registration pages as they often contain organizer contact info
        - If you find multiple email addresses, prioritize ones related to event organization
        - Note any specific contact preferences or registration procedures mentioned
        
        Return the information as JSON in this format:
        {{
            "primary_contact_method": "email|form|social|phone",
            "contact_email": "example@domain.com",
            "contact_form_url": "https://full.url.to/contact/form",
            "social_media_contact": "URL to best social media contact method",
            "phone": "phone number if available",
            "contact_notes": "Any important notes about contacting this organizer",
            "source_url": "URL where this contact info was found",
            "source_type": "event_website|organizer_website",
            "confidence_score": 0.95,  // How confident are you in this being the correct contact (0-1)
            "registration_specific": true  // Whether this is specifically for event registration
        }}

        Before returning:
        1. Verify that any URLs are complete (not relative paths) and accessible
        2. If you find contact info on multiple pages, choose the most relevant for event organization
        3. Include any special instructions about contacting in the notes
        4. If you're not highly confident about the contact information, explain why in the notes

        Do not return any comments in the JSON file! Return plain JSON.
        """

        try:
            response = agent.chat(prompt)

            # Extract JSON from the response
            json_text = response.response
            # Find the JSON content between triple backticks if present
            json_match = re.search(r"```json\s*(.*?)\s*```", json_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)

            try:
                contact_data = json.loads(json_text)
            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse JSON response for {organizer.name}: {str(e)}"
                )
                logger.error(f"Raw response: {json_text}")
                return None

            # Update the organizer with the found information
            if isinstance(contact_data, dict):
                organizer.contact_email = contact_data.get("contact_email")
                organizer.contact_form_url = contact_data.get("contact_form_url")

                notes = []
                if contact_data.get("source_url"):
                    notes.append(f"Found on: {contact_data['source_url']}")
                if contact_data.get("contact_notes"):
                    notes.append(contact_data["contact_notes"])
                if contact_data.get("registration_specific"):
                    notes.append("This contact is specifically for event registration")

                organizer.contact_notes = "\n".join(notes)

                # Set status based on confidence and found information
                confidence = contact_data.get("confidence_score", 0)
                if confidence >= 0.8:
                    organizer.contact_status = "pending"
                else:
                    organizer.contact_status = "needs_review"

                organizer.save()
                logger.info(f"Successfully updated contact info for: {organizer.name}")
                return contact_data
            else:
                logger.error(f"Invalid response format for organizer: {organizer.name}")
                return None

        except Exception as e:
            logger.error(f"Error processing organizer {organizer.name}: {str(e)}")
            return None
