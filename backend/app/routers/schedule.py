from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Plant as PlantModel
from ..schemas import ScheduledPlant

router = APIRouter(tags=["schedule"])


@router.get("/schedule", response_model=list[ScheduledPlant])
def get_schedule(due_today: bool = False, db: Session = Depends(get_db)):
    now = datetime.now(tz=timezone.utc)
    query = db.query(PlantModel).filter(PlantModel.next_watering.isnot(None))

    if due_today:
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        query = query.filter(PlantModel.next_watering <= tomorrow)

    return query.order_by(PlantModel.next_watering).all()
