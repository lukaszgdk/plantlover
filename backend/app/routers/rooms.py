import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Room as RoomModel, Plant as PlantModel
from ..schemas import Room, RoomCreate, Plant

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[Room])
def list_rooms(db: Session = Depends(get_db)):
    return db.query(RoomModel).order_by(RoomModel.name).all()


@router.post("", response_model=Room, status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    room = RoomModel(**payload.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("/{room_id}/plants", response_model=list[Plant])
def list_plants_in_room(room_id: uuid.UUID, db: Session = Depends(get_db)):
    room = db.get(RoomModel, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return (
        db.query(PlantModel)
        .filter(PlantModel.room_id == room_id)
        .order_by(PlantModel.name)
        .all()
    )
