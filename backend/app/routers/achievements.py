from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Achievement, UserAchievement

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get("")
def list_achievements(db: Session = Depends(get_db)):
    all_achievements = db.query(Achievement).order_by(Achievement.condition_type, Achievement.condition_value).all()
    unlocked_keys = {ua.achievement_key for ua in db.query(UserAchievement).all()}
    unlocked_map = {
        ua.achievement_key: ua.unlocked_at
        for ua in db.query(UserAchievement).all()
    }

    return [
        {
            "key": a.key,
            "name": a.name,
            "description": a.description,
            "icon": a.icon,
            "unlocked": a.key in unlocked_keys,
            "unlocked_at": unlocked_map.get(a.key),
        }
        for a in all_achievements
    ]
