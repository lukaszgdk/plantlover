import uuid
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel


SunlightLevel = Literal["low", "medium", "high"]


class PlantBase(BaseModel):
    name: str
    species: str | None = None
    photo_url: str | None = None
    watering_interval_days: int | None = None
    last_watered: date | None = None
    sunlight: SunlightLevel | None = None
    notes: str | None = None


class PlantCreate(PlantBase):
    pass


class PlantUpdate(PlantBase):
    name: str | None = None


class Plant(PlantBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class IdentifyRequest(BaseModel):
    image_base64: str


class IdentifyResponse(BaseModel):
    plant_id: uuid.UUID
    identified_species: str
    confidence: float
    notes: str


class CareLogRequest(BaseModel):
    event_type: Literal["watering", "fertilizing"]
    notes: str | None = None


class CareLogResponse(BaseModel):
    plant_id: uuid.UUID
    event_type: str
    message: str
