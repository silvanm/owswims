"""
Pydantic schemas for MCP tool inputs/outputs.
"""
from datetime import date as date_type, time as time_type
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field


# Event schemas
class EventCreate(BaseModel):
    name: str = Field(..., max_length=100, description="Event name")
    date_start: date_type = Field(..., description="Start date")
    date_end: date_type = Field(..., description="End date")
    website: Optional[str] = Field(
        None, max_length=200, description="Event website URL"
    )
    description: Optional[str] = Field(
        None, max_length=2048, description="Public description"
    )
    location_id: Optional[int] = Field(None, description="Location ID")
    organizer_id: Optional[int] = Field(None, description="Organizer ID")
    cancelled: Optional[bool] = Field(False, description="Is event cancelled")
    invisible: Optional[bool] = Field(False, description="Hide from public")
    water_temp: Optional[float] = Field(
        None, description="Water temperature in Celsius"
    )
    needs_medical_certificate: Optional[bool] = Field(None)
    needs_license: Optional[bool] = Field(None)


class EventUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    date_start: Optional[date_type] = None
    date_end: Optional[date_type] = None
    website: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2048)
    location_id: Optional[int] = None
    organizer_id: Optional[int] = None
    cancelled: Optional[bool] = None
    invisible: Optional[bool] = None
    water_temp: Optional[float] = None
    needs_medical_certificate: Optional[bool] = None
    needs_license: Optional[bool] = None
    sold_out: Optional[bool] = None


class RaceInfo(BaseModel):
    id: int
    date: date_type
    race_time: Optional[time_type] = None
    distance: float
    name: Optional[str] = None
    wetsuit: Optional[str] = None


class LocationInfo(BaseModel):
    id: int
    city: str
    country: str
    water_name: Optional[str] = None
    water_type: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class OrganizerInfo(BaseModel):
    id: int
    name: str
    website: Optional[str] = None


class EventResponse(BaseModel):
    id: int
    name: str
    date_start: date_type
    date_end: date_type
    website: str
    description: str
    cancelled: bool
    invisible: bool
    water_temp: Optional[float] = None
    needs_medical_certificate: Optional[bool] = None
    needs_license: Optional[bool] = None
    sold_out: Optional[bool] = None
    location: Optional[LocationInfo] = None
    organizer: Optional[OrganizerInfo] = None
    races: Optional[List[RaceInfo]] = None


# Race schemas
class RaceCreate(BaseModel):
    event_id: int = Field(..., description="Parent event ID")
    race_date: date_type = Field(..., description="Race date")
    distance: float = Field(..., description="Distance in km")
    race_time: Optional[time_type] = Field(None, description="Start time")
    name: Optional[str] = Field(None, max_length=50, description="Race name/category")
    wetsuit: Optional[str] = Field(
        None, description="Wetsuit policy: compulsory, optional, prohibited"
    )
    price: Optional[Decimal] = Field(None, description="Entry price in EUR")


class RaceUpdate(BaseModel):
    race_date: Optional[date_type] = None
    distance: Optional[float] = None
    race_time: Optional[time_type] = None
    name: Optional[str] = Field(None, max_length=50)
    wetsuit: Optional[str] = None
    price: Optional[Decimal] = None


class RaceResponse(BaseModel):
    id: int
    event_id: int
    race_date: date_type
    distance: float
    race_time: Optional[time_type] = None
    name: Optional[str] = None
    wetsuit: Optional[str] = None
    price: Optional[str] = None  # MoneyField serializes as string


# Location schemas
class LocationCreate(BaseModel):
    city: str = Field(..., max_length=100, description="City name")
    country: str = Field(
        ..., max_length=2, description="Country code (2-letter ISO)"
    )
    water_name: Optional[str] = Field(
        None, max_length=100, description="Water body name"
    )
    water_type: Optional[str] = Field(
        None, description="Type: river, sea, lake, pool"
    )
    lat: Optional[float] = Field(None, description="Latitude")
    lng: Optional[float] = Field(None, description="Longitude")
    address: Optional[str] = Field(None, max_length=200, description="Street address")


class LocationUpdate(BaseModel):
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=2)
    water_name: Optional[str] = Field(None, max_length=100)
    water_type: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = Field(None, max_length=200)


class LocationResponse(BaseModel):
    id: int
    city: str
    country: str
    water_name: Optional[str] = None
    water_type: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    average_rating: Optional[float] = None


# Organizer schemas
class OrganizerCreate(BaseModel):
    name: str = Field(..., max_length=100, description="Organizer name")
    website: str = Field(..., max_length=200, description="Organizer website URL")
    contact_email: Optional[str] = Field(None, description="Contact email")
    language: Optional[str] = Field(
        None, max_length=5, description="ISO language code (e.g., 'en', 'de')"
    )


class OrganizerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    contact_email: Optional[str] = None
    language: Optional[str] = Field(None, max_length=5)
    contact_form_url: Optional[str] = Field(None, max_length=200)


class OrganizerResponse(BaseModel):
    id: int
    name: str
    website: str
    slug: Optional[str] = None
    contact_email: Optional[str] = None
    language: Optional[str] = None
    contact_form_url: Optional[str] = None
