from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Plant as PlantModel
from ..schemas import ScheduledPlant

router = APIRouter(tags=["schedule"])


@router.get("/schedule", response_model=list[ScheduledPlant])
def get_schedule(due_today: bool = False, db: Session = Depends(get_db)):
    now = datetime.now(tz=timezone.utc)

    if due_today:
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        # Include: overdue/due-today plants AND never-watered plants that have an interval set
        return (
            db.query(PlantModel)
            .filter(
                or_(
                    PlantModel.next_watering <= tomorrow,
                    PlantModel.last_watered.is_(None),
                )
            )
            .order_by(PlantModel.next_watering.nullsfirst(), PlantModel.name)
            .all()
        )

    # Calendar view: all plants with a scheduled next watering
    return (
        db.query(PlantModel)
        .filter(PlantModel.next_watering.isnot(None))
        .order_by(PlantModel.next_watering)
        .all()
    )
