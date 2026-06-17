import os
import uuid
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CareLog as CareLogModel
from ..models import Plant as PlantModel
from ..schemas import (
    CareLogCreate,
    CareLogEntry,
    IdentifyResponse,
    IdentifyResult,
    Plant,
    PlantCreate,
    PlantUpdate,
    ScheduledPlant,
    WaterResponse,
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
def identify_plant(
    plant_id: uuid.UUID,
    image: UploadFile = File(...),
    organ: str = Form(default="auto"),
    db: Session = Depends(get_db),
):
    plant = get_plant_or_404(plant_id, db)
    api_key = os.environ["PLANTNET_API_KEY"]

    content = image.file.read()
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"https://my-api.plantnet.org/v2/identify/all?api-key={api_key}&lang=en",
            files=[("images", (image.filename or "photo.jpg", content, image.content_type))],
            data={"organs": [organ]},
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"PlantNet API error: {resp.text[:200]}")

    data = resp.json()
    results = data.get("results", [])
    if not results:
        raise HTTPException(status_code=422, detail="No plant identified in the image")

    top = results[0]
    species = top["species"]["scientificNameWithoutAuthor"]
    common_names = top["species"].get("commonNames") or []
    common_name = common_names[0] if common_names else None
    score = top["score"]

    plant.species = species
    plant.common_name = common_name
    db.commit()

    top5 = [
        IdentifyResult(
            species=r["species"]["scientificNameWithoutAuthor"],
            common_name=((r["species"].get("commonNames") or [None])[0]),
            score=r["score"],
        )
        for r in results[:5]
    ]

    return IdentifyResponse(species=species, common_name=common_name, score=score, all_results=top5)


@router.post("/{plant_id}/water", response_model=WaterResponse)
def water_plant(plant_id: uuid.UUID, db: Session = Depends(get_db)):
    plant = get_plant_or_404(plant_id, db)
    now = datetime.now(tz=timezone.utc)
    plant.last_watered = now
    plant.next_watering = (
        now + timedelta(days=plant.watering_interval_days)
        if plant.watering_interval_days
        else None
    )
    db.commit()
    db.refresh(plant)
    return WaterResponse(
        plant_id=plant.id,
        last_watered=plant.last_watered,
        next_watering=plant.next_watering,
    )


@router.post("/{plant_id}/care-log", response_model=CareLogEntry, status_code=status.HTTP_201_CREATED)
def log_care_event(
    plant_id: uuid.UUID, payload: CareLogCreate, db: Session = Depends(get_db)
):
    plant = get_plant_or_404(plant_id, db)
    now = datetime.now(tz=timezone.utc)

    if payload.action == "watered":
        plant.last_watered = now
        plant.next_watering = (
            now + timedelta(days=plant.watering_interval_days)
            if plant.watering_interval_days
            else None
        )

    entry = CareLogModel(
        id=uuid.uuid4(),
        plant_id=plant.id,
        action=payload.action,
        notes=payload.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/{plant_id}/care-log", response_model=list[CareLogEntry])
def get_care_log(plant_id: uuid.UUID, db: Session = Depends(get_db)):
    get_plant_or_404(plant_id, db)
    return (
        db.query(CareLogModel)
        .filter(CareLogModel.plant_id == plant_id)
        .order_by(CareLogModel.logged_at.desc())
        .limit(20)
        .all()
    )


