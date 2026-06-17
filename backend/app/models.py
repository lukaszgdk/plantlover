import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    species: Mapped[str | None] = mapped_column(String(255))
    common_name: Mapped[str | None] = mapped_column(String(255))
    photo_url: Mapped[str | None] = mapped_column(String(1024))
    watering_interval_days: Mapped[int | None] = mapped_column(Integer)
    last_watered: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    next_watering: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sunlight: Mapped[str | None] = mapped_column(String(16))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    care_logs: Mapped[list["CareLog"]] = relationship(
        "CareLog", back_populates="plant", cascade="all, delete-orphan"
    )


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
