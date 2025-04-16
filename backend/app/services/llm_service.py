import logging
from typing import Optional, TypeVar, Generic, Type
from django.conf import settings
from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def get_completion(self, prompt: str) -> str:
        """Get completion from GPT-4"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates professional email content.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error getting completion from OpenAI: {str(e)}")
            return "Error generating email content. Please try again."

    def parse_completion(
        self, prompt: str, response_model: Type[T], system_prompt: str = None
    ) -> T:
        """Get structured completion from GPT-4 using the parse API"""
        try:
            system_content = (
                system_prompt
                or "You are a helpful assistant that extracts structured information."
            )

            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_content,
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format=response_model,
            )
            return response.choices[0].message.parsed
        except Exception as e:
            logger.error(f"Error parsing completion from OpenAI: {str(e)}")
            # Return a default instance of the model
            return response_model()
