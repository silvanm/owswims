import logging
from typing import Optional, TypeVar, Generic, Type, List
from django.conf import settings
from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def _supports_reasoning_effort(self) -> bool:
        """Check if the current model supports reasoning_effort parameter."""
        return self.model.startswith("gpt-5")

    def get_completion(self, prompt: str) -> str:
        """Get completion from GPT-4/GPT-5"""
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates professional email content.",
                    },
                    {"role": "user", "content": prompt},
                ],
            }
            if self._supports_reasoning_effort():
                kwargs["reasoning_effort"] = settings.OPENAI_REASONING_EFFORT

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error getting completion from OpenAI: {str(e)}")
            return "Error generating email content. Please try again."

    def parse_completion(
        self, prompt: str, response_model: Type[T], system_prompt: str = None
    ) -> T:
        """Get structured completion from GPT-4/GPT-5 using the parse API"""
        try:
            system_content = (
                system_prompt
                or "You are a helpful assistant that extracts structured information."
            )

            kwargs = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_content,
                    },
                    {"role": "user", "content": prompt},
                ],
                "response_format": response_model,
            }
            if self._supports_reasoning_effort():
                kwargs["reasoning_effort"] = settings.OPENAI_REASONING_EFFORT

            response = self.client.beta.chat.completions.parse(**kwargs)
            return response.choices[0].message.parsed
        except Exception as e:
            logger.error(f"Error parsing completion from OpenAI: {str(e)}")
            # Return a default instance of the model
            return response_model()

    def parse_vision_completion(
        self,
        messages: List[dict],
        response_model: Type[T],
        system_prompt: str = None,
    ) -> T:
        """Get structured completion from a vision prompt (text + images).

        Args:
            messages: OpenAI-style messages with multi-content blocks
                      (text and image_url entries).
            response_model: Pydantic model for structured output.
            system_prompt: Optional system prompt override.
        """
        try:
            system_content = (
                system_prompt
                or "You are a helpful assistant that extracts structured information."
            )

            all_messages = [
                {"role": "system", "content": system_content},
                *messages,
            ]

            kwargs = {
                "model": self.model,
                "messages": all_messages,
                "response_format": response_model,
            }
            if self._supports_reasoning_effort():
                kwargs["reasoning_effort"] = settings.OPENAI_REASONING_EFFORT

            response = self.client.beta.chat.completions.parse(**kwargs)
            return response.choices[0].message.parsed
        except Exception as e:
            logger.error(f"Error parsing vision completion from OpenAI: {str(e)}")
            return response_model()
