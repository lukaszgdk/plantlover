import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class Achievement(Base):
    __tablename__ = "achievements"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(16), nullable=False)
    condition_type: Mapped[str] = mapped_column(String(64), nullable=False)
    condition_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    unlocks: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    achievement_key: Mapped[str] = mapped_column(String(64), ForeignKey("achievements.key"), nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    plant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plants.id", ondelete="SET NULL"), nullable=True
    )

    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="unlocks")
    plant: Mapped["Plant | None"] = relationship("Plant")


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(32))

    plants: Mapped[list["Plant"]] = relationship("Plant", back_populates="room")


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    species: Mapped[str | None] = mapped_column(String(255))
    common_name: Mapped[str | None] = mapped_column(String(255))
    photo_url: Mapped[str | None] = mapped_column(String(1024))
    user_photo_url: Mapped[str | None] = mapped_column(String(1024))
    wiki_url: Mapped[str | None] = mapped_column(String(1024))
    plant_info: Mapped[str | None] = mapped_column(Text)
    watering_interval_days: Mapped[int | None] = mapped_column(Integer)
    last_watered: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_watering: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sunlight: Mapped[str | None] = mapped_column(String(16))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    room_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True
    )

    care_logs: Mapped[list["CareLog"]] = relationship(
        "CareLog", back_populates="plant", cascade="all, delete-orphan"
    )
    room: Mapped["Room | None"] = relationship("Room", back_populates="plants")


class CareLog(Base):
    __tablename__ = "care_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("plants.id", ondelete="CASCADE"), nullable=False
    )
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    plant: Mapped["Plant"] = relationship("Plant", back_populates="care_logs")
