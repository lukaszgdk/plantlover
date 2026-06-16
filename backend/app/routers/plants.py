import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Plant as PlantModel
from ..schemas import (
    Plant,
    PlantCreate,
    PlantUpdate,
    IdentifyRequest,
    IdentifyResponse,
    CareLogRequest,
    CareLogResponse,
)

router = APIRouter(prefix="/plants", tags=["plants"])


def get_plant_or_404(plant_id: uuid.UUID, db: Session) -> PlantModel:
    plant = db.get(PlantModel, plant_id)
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


@router.get("", response_model=list[Plant])
def list_plants(db: Session = Depends(get_db)):
    return db.query(PlantModel).order_by(PlantModel.created_at.desc()).all()


@router.post("", response_model=Plant, status_code=status.HTTP_201_CREATED)
def create_plant(payload: PlantCreate, db: Session = Depends(get_db)):
    plant = PlantModel(**payload.model_dump())
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


@router.get("/{plant_id}", response_model=Plant)
def get_plant(plant_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_plant_or_404(plant_id, db)


@router.put("/{plant_id}", response_model=Plant)
def update_plant(plant_id: uuid.UUID, payload: PlantUpdate, db: Session = Depends(get_db)):
    plant = get_plant_or_404(plant_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plant, field, value)
    db.commit()
    db.refresh(plant)
    return plant


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plant(plant_id: uuid.UUID, db: Session = Depends(get_db)):
    plant = get_plant_or_404(plant_id, db)
    db.delete(plant)
    db.commit()


@router.post("/{plant_id}/identify", response_model=IdentifyResponse)
def identify_plant(plant_id: uuid.UUID, payload: IdentifyRequest, db: Session = Depends(get_db)):
    plant = get_plant_or_404(plant_id, db)
    # Mock identification — replace with real vision model call
    identified = "Monstera deliciosa"
    plant.species = identified
    db.commit()
    return IdentifyResponse(
        plant_id=plant.id,
        identified_species=identified,
        confidence=0.92,
        notes="Mock identification result. Integrate a real plant ID API to replace this.",
    )


@router.post("/{plant_id}/care-log", response_model=CareLogResponse)
def log_care_event(plant_id: uuid.UUID, payload: CareLogRequest, db: Session = Depends(get_db)):
    plant = get_plant_or_404(plant_id, db)
    if payload.event_type == "watering":
        from datetime import date
        plant.last_watered = date.today()
        db.commit()
    return CareLogResponse(
        plant_id=plant.id,
        event_type=payload.event_type,
        message=f"Logged {payload.event_type} event for {plant.name}.",
    )
