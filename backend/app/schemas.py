import uuid
from datetime import date, datetime
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
    plant_info: str | None = None
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
    plant_info: str | None = None
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
    reference_image_url: str | None = None
    gbif_id: str | None = None


class IdentifyResponse(BaseModel):
    species: str
    common_name: str | None
    score: float
    all_results: list[IdentifyResult]


class IdentifyNewResponse(BaseModel):
    top: IdentifyResult
    alternatives: list[IdentifyResult]


# ── Species care ──────────────────────────────────────────────────────────────
class SpeciesCare(BaseModel):
    watering_days: int | None
    sunlight: str | None
    source: str  # "database" | "not_found"


# ── App config ────────────────────────────────────────────────────────────────
class AppConfig(BaseModel):
    setup_completed: bool = False
    plantnet_api_key: str | None = None
    perenual_api_key: str | None = None
    discord_bot_token: str | None = None
    discord_channel_id: str | None = None
    reminder_times: list[str] = ["08:00", "15:00", "20:00"]


class AppConfigPublic(BaseModel):
    """Config without sensitive values (masked)."""
    setup_completed: bool
    plantnet_api_key_set: bool
    perenual_api_key_set: bool
    discord_bot_token_set: bool
    discord_channel_id: str | None
    reminder_times: list[str]


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
    watered_at: date | None = None


class CareLogEntry(BaseModel):
    id: uuid.UUID
    plant_id: uuid.UUID
    logged_at: datetime
    action: str
    notes: str | None

    model_config = {"from_attributes": True}
