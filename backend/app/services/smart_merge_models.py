from pydantic import BaseModel, Field
from typing import Literal


class MergeDecision(BaseModel):
    keep_location: Literal["A", "B"] = Field(
        default="A",
        description="Which location to keep: A or B. "
        "Prefer the location closer to a body of water "
        "visible on the satellite map.",
    )
    keep_event: Literal["A", "B"] = Field(
        default="A",
        description="Which event to keep as the primary "
        "event: A or B. Prefer the event with more races, "
        "better data quality, or verified status.",
    )
    location_reasoning: str = Field(
        default="",
        description="Brief explanation of why this location "
        "was chosen (e.g. closer to water, better "
        "coordinates).",
    )
    event_reasoning: str = Field(
        default="",
        description="Brief explanation of why this event was "
        "chosen as primary (e.g. more races, verified, "
        "richer data).",
    )
    merge_races: bool = Field(
        default=True,
        description="Whether to transfer races from the "
        "secondary event to the primary.",
    )
    merge_description: bool = Field(
        default=False,
        description="Whether to copy the description from "
        "the secondary event if the primary lacks one.",
    )
    merge_website: bool = Field(
        default=False,
        description="Whether to copy the website from the "
        "secondary event if the primary lacks one.",
    )
    merge_flyer: bool = Field(
        default=False,
        description="Whether to copy the flyer image from "
        "the secondary event if the primary lacks one.",
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score (0-1) for this merge "
        "decision.",
    )
