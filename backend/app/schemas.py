import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


SunlightLevel = Literal["low", "medium", "high"]


# ── Room ──────────────────────────────────────────────────────────────────────
class RoomBase(BaseModel):
    name: str
    icon: str | None = None


class RoomCreate(RoomBase):
    pass


class Room(RoomBase):
    id: uuid.UUID
    model_config = {"from_attributes": True}


# ── Plant ─────────────────────────────────────────────────────────────────────
class PlantBase(BaseModel):
    name: str
    species: str | None = None
    common_name: str | None = None
    photo_url: str | None = None
    watering_interval_days: int | None = None
    last_watered: datetime | None = None
    next_watering: datetime | None = None
    sunlight: SunlightLevel | None = None
    notes: str | None = None
    room_id: uuid.UUID | None = None


class PlantCreate(PlantBase):
    pass


class PlantUpdate(BaseModel):
    name: str | None = None
    species: str | None = None
    common_name: str | None = None
    photo_url: str | None = None
    watering_interval_days: int | None = None
    last_watered: datetime | None = None
    next_watering: datetime | None = None
    sunlight: SunlightLevel | None = None
    notes: str | None = None
    room_id: uuid.UUID | None = None


class Plant(PlantBase):
    id: uuid.UUID
    created_at: datetime
    room: Room | None = None

    model_config = {"from_attributes": True}


# ── Identify ──────────────────────────────────────────────────────────────────
class IdentifyResult(BaseModel):
    species: str
    common_name: str | None
    score: float


class IdentifyResponse(BaseModel):
    species: str
    common_name: str | None
    score: float
    all_results: list[IdentifyResult]


class IdentifyNewResponse(BaseModel):
    top: IdentifyResult
    alternatives: list[IdentifyResult]


# ── Watering ──────────────────────────────────────────────────────────────────
class WaterResponse(BaseModel):
    plant_id: uuid.UUID
    last_watered: datetime
    next_watering: datetime | None


# ── Schedule ──────────────────────────────────────────────────────────────────
class ScheduledPlant(BaseModel):
    id: uuid.UUID
    name: str
    species: str | None
    photo_url: str | None
    next_watering: datetime | None
    last_watered: datetime | None
    room: Room | None = None

    model_config = {"from_attributes": True}


# ── Care log ──────────────────────────────────────────────────────────────────
class CareLogCreate(BaseModel):
    action: str
    notes: str | None = None


class CareLogEntry(BaseModel):
    id: uuid.UUID
    plant_id: uuid.UUID
    logged_at: datetime
    action: str
    notes: str | None

    model_config = {"from_attributes": True}
