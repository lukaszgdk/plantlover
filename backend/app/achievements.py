"""Logika sprawdzania i odblokowywania achievementów."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from .models import Achievement, UserAchievement, CareLog, Plant


def _already_unlocked(db: Session, key: str) -> bool:
    return db.query(UserAchievement).filter_by(achievement_key=key).first() is not None


def _unlock(db: Session, key: str, plant_id=None) -> UserAchievement | None:
    if _already_unlocked(db, key):
        return None
    ua = UserAchievement(
        id=uuid.uuid4(),
        achievement_key=key,
        unlocked_at=datetime.now(timezone.utc),
        plant_id=plant_id,
    )
    db.add(ua)
    return ua


def check_and_unlock(db: Session, plant: Plant, watered_at: datetime) -> list[str]:
    """Sprawdza warunki po podlaniu rośliny. Zwraca listę kluczy nowo odblokowanych achievementów."""
    newly_unlocked: list[str] = []

    def _try(key: str, plant_id=None):
        ua = _unlock(db, key, plant_id)
        if ua:
            newly_unlocked.append(key)

    total_waterings = db.query(CareLog).filter_by(action="watered").count()
    plant_count = db.query(Plant).count()
    room_count = (
        db.query(Plant.room_id)
        .filter(Plant.room_id.isnot(None))
        .distinct()
        .count()
    )

    # Całkowita liczba podlewań
    if total_waterings >= 1:
        _try("first_watering", plant.id)
    if total_waterings >= 10:
        _try("watering_10")
    if total_waterings >= 50:
        _try("watering_50")
    if total_waterings >= 100:
        _try("watering_100")

    # Liczba roślin
    if plant_count >= 5:
        _try("collector_5")
    if plant_count >= 10:
        _try("collector_10")

    # Rośliny w co najmniej 3 pokojach
    if room_count >= 3:
        _try("all_rooms")

    # Nocne podlewanie (22:00–6:00)
    hour = watered_at.hour
    if hour >= 22 or hour < 6:
        _try("night_watering", plant.id)

    # Ratownik — podlanie >3 dni po terminie
    if plant.next_watering:
        next_w = plant.next_watering
        if next_w.tzinfo is None:
            next_w = next_w.replace(tzinfo=timezone.utc)
        days_late = (watered_at - next_w).days
        if days_late >= 3:
            _try("rescuer", plant.id)

    # Passa dzienna — min. 1 podlewanie przez N dni z rzędu
    _check_day_streak(db, watered_at, newly_unlocked)

    # Passa na czas dla konkretnej rośliny
    _check_on_time_streak(db, plant, watered_at, newly_unlocked)

    db.flush()
    return newly_unlocked


def _check_day_streak(db: Session, watered_at: datetime, newly_unlocked: list[str]):
    """Sprawdza czy jest N-dniowa passa podlewania (min. 1 raz dziennie)."""
    logs = (
        db.query(CareLog)
        .filter_by(action="watered")
        .order_by(CareLog.logged_at.desc())
        .all()
    )
    if not logs:
        return

    days_with_watering: set[str] = {l.logged_at.strftime("%Y-%m-%d") for l in logs}

    streak = 0
    day = watered_at.date()
    while day.strftime("%Y-%m-%d") in days_with_watering:
        streak += 1
        day -= timedelta(days=1)

    if streak >= 30 and not _already_unlocked(db, "month_streak"):
        ua = _unlock(db, "month_streak")
        if ua:
            newly_unlocked.append("month_streak")
    if streak >= 7 and not _already_unlocked(db, "week_streak"):
        ua = _unlock(db, "week_streak")
        if ua:
            newly_unlocked.append("week_streak")


def _check_on_time_streak(db: Session, plant: Plant, watered_at: datetime, newly_unlocked: list[str]):
    """Sprawdza passę podlewań na czas dla danej rośliny."""
    logs = (
        db.query(CareLog)
        .filter_by(plant_id=plant.id, action="watered")
        .order_by(CareLog.logged_at.desc())
        .limit(14)
        .all()
    )

    if not plant.watering_interval_days or len(logs) < 2:
        return

    interval = timedelta(days=plant.watering_interval_days)
    # Tolerancja: do 1 dnia spóźnienia
    tolerance = timedelta(days=1)

    streak = 0
    for i in range(len(logs) - 1):
        gap = logs[i].logged_at - logs[i + 1].logged_at
        if gap <= interval + tolerance:
            streak += 1
        else:
            break

    if streak >= 14 and not _already_unlocked(db, "on_time_14"):
        ua = _unlock(db, "on_time_14", plant.id)
        if ua:
            newly_unlocked.append("on_time_14")
    elif streak >= 5 and not _already_unlocked(db, "on_time_5"):
        ua = _unlock(db, "on_time_5", plant.id)
        if ua:
            newly_unlocked.append("on_time_5")
