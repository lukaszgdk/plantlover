import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CareLog as CareLogModel
from ..models import Plant as PlantModel
from ..schemas import (
    CareLogCreate,
    CareLogEntry,
    IdentifyNewResponse,
    IdentifyResponse,
    IdentifyResult,
    Plant,
    PlantUpdate,
    SpeciesCare,
    WaterResponse,
)
from ..species_care import lookup as lookup_care

router = APIRouter(prefix="/plants", tags=["plants"])

UPLOADS_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def get_plant_or_404(plant_id: uuid.UUID, db: Session) -> PlantModel:
    plant = db.get(PlantModel, plant_id)
    if not plant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant


def _save_upload(file: UploadFile, content: bytes) -> str:
    ext = Path(file.filename or "photo.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    (UPLOADS_DIR / filename).write_bytes(content)
    return f"/uploads/{filename}"


def _save_bytes(content: bytes, ext: str = ".jpg") -> str:
    filename = f"{uuid.uuid4()}{ext}"
    (UPLOADS_DIR / filename).write_bytes(content)
    return f"/uploads/{filename}"


def _call_plantnet(image_bytes: list[bytes], filenames: list[str]) -> dict:
    api_key = os.environ.get("PLANTNET_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="PlantNet API key not configured. Go to Settings to add it.")
    files = [("images", (fn, data, "image/jpeg")) for data, fn in zip(image_bytes, filenames)]
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"https://my-api.plantnet.org/v2/identify/all?api-key={api_key}&lang=pl",
            files=files,
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"PlantNet API error: {resp.text[:200]}")
    return resp.json()


def _parse_results(data: dict) -> list[IdentifyResult]:
    results = []
    for r in data.get("results", []):
        images = r.get("images", [])
        ref_image = images[0]["url"].get("m") if images else None
        gbif = r["species"].get("gbif", {})
        results.append(IdentifyResult(
            species=r["species"]["scientificNameWithoutAuthor"],
            common_name=((r["species"].get("commonNames") or [None])[0]),
            score=r["score"],
            reference_image_url=ref_image,
            gbif_id=str(gbif["id"]) if gbif.get("id") else None,
        ))
    return results


# ── GET /plants/species-care ──────────────────────────────────────────────────
@router.get("/species-care", response_model=SpeciesCare)
def get_species_care(species: str):
    care = lookup_care(species)
    if care:
        return SpeciesCare(watering_days=care["watering_days"], sunlight=care["sunlight"], source="database")
    return SpeciesCare(watering_days=None, sunlight=None, source="not_found")


# ── POST /plants/identify-new ─────────────────────────────────────────────────
# Defined before /{plant_id} routes to prevent routing ambiguity
@router.post("/identify-new", response_model=IdentifyNewResponse)
def identify_new(images: list[UploadFile] = File(...)):
    if not images:
        raise HTTPException(status_code=400, detail="At least one image is required")
    contents = [img.file.read() for img in images]
    filenames = [img.filename or f"photo{i}.jpg" for i, img in enumerate(images)]
    results = _parse_results(_call_plantnet(contents, filenames))
    if not results:
        raise HTTPException(status_code=422, detail="No plant identified in the images")
    return IdentifyNewResponse(top=results[0], alternatives=results[1:6])


# ── GET /plants ────────────────────────────────────────────────────────────────
@router.get("", response_model=list[Plant])
def list_plants(db: Session = Depends(get_db)):
    return db.query(PlantModel).order_by(PlantModel.created_at.desc()).all()


# ── POST /plants (multipart form + optional photo file) ───────────────────────
@router.post("", response_model=Plant, status_code=status.HTTP_201_CREATED)
async def create_plant(
    name: str = Form(...),
    species: str | None = Form(None),
    common_name: str | None = Form(None),
    photo_url: str | None = Form(None),
    watering_interval_days: int | None = Form(None),
    sunlight: str | None = Form(None),
    notes: str | None = Form(None),
    room_id: str | None = Form(None),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    final_photo_url = photo_url or None
    if photo and photo.filename:
        content = await photo.read()
        final_photo_url = _save_upload(photo, content)

    plant = PlantModel(
        name=name,
        species=species or None,
        common_name=common_name or None,
        photo_url=final_photo_url,
        watering_interval_days=watering_interval_days,
        sunlight=sunlight or None,
        notes=notes or None,
        room_id=uuid.UUID(room_id) if room_id else None,
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


# ── GET /plants/{plant_id} ─────────────────────────────────────────────────────
@router.get("/{plant_id}", response_model=Plant)
def get_plant(plant_id: uuid.UUID, db: Session = Depends(get_db)):
    return get_plant_or_404(plant_id, db)


# ── PUT /plants/{plant_id} ─────────────────────────────────────────────────────
@router.put("/{plant_id}", response_model=Plant)
def update_plant(plant_id: uuid.UUID, payload: PlantUpdate, db: Session = Depends(get_db)):
    plant = get_plant_or_404(plant_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plant, field, value)
    db.commit()
    db.refresh(plant)
    return plant


# ── PATCH /plants/{plant_id} ──────────────────────────────────────────────────
@router.patch("/{plant_id}", response_model=Plant)
def patch_plant(plant_id: uuid.UUID, payload: PlantUpdate, db: Session = Depends(get_db)):
    plant = get_plant_or_404(plant_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plant, field, value)
    db.commit()
    db.refresh(plant)
    return plant


# ── DELETE /plants/{plant_id} ─────────────────────────────────────────────────
@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plant(plant_id: uuid.UUID, db: Session = Depends(get_db)):
    plant = get_plant_or_404(plant_id, db)
    db.delete(plant)
    db.commit()


# ── POST /plants/{plant_id}/identify ─────────────────────────────────────────
@router.post("/{plant_id}/identify", response_model=IdentifyResponse)
def identify_plant(
    plant_id: uuid.UUID,
    image: UploadFile = File(...),
    organ: str = Form(default="auto"),
    db: Session = Depends(get_db),
):
    plant = get_plant_or_404(plant_id, db)
    content = image.file.read()
    results = _parse_results(_call_plantnet([content], [image.filename or "photo.jpg"]))
    if not results:
        raise HTTPException(status_code=422, detail="No plant identified in the image")

    top = results[0]
    plant.species = top.species
    plant.common_name = top.common_name
    db.commit()

    return IdentifyResponse(
        species=top.species,
        common_name=top.common_name,
        score=top.score,
        all_results=results[:5],
    )


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
        watered_at = (
            datetime(payload.watered_at.year, payload.watered_at.month, payload.watered_at.day,
                     tzinfo=timezone.utc)
            if payload.watered_at else now
        )
        plant.last_watered = watered_at
        plant.next_watering = (
            watered_at + timedelta(days=plant.watering_interval_days)
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


@router.post("/{plant_id}/fetch-wiki", response_model=Plant)
def fetch_wiki(plant_id: uuid.UUID, db: Session = Depends(get_db)):
    plant = get_plant_or_404(plant_id, db)
    if not plant.species:
        raise HTTPException(status_code=400, detail="Plant has no species set")

    headers = {"User-Agent": "PlantLover/1.0 (plant care app)"}
    ref_image_url: str | None = None
    species_page_url: str | None = None

    def _wikipedia_thumb(http: httpx.Client, query: str) -> tuple[str | None, str | None]:
        """Try Wikipedia page thumbnail first — fast, good quality."""
        resp = http.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query", "titles": query.replace(" ", "_"),
                "prop": "pageimages|info", "pithumbsize": 800,
                "inprop": "url", "format": "json", "formatversion": 2,
            },
            headers=headers,
        )
        if not resp.is_success:
            return None, None
        for page in resp.json().get("query", {}).get("pages", []):
            if page.get("missing"):
                continue
            image_url = (page.get("thumbnail") or {}).get("source")
            page_url = page.get("fullurl")
            if image_url:
                return image_url, page_url
        return None, None

    def _commons_search(http: httpx.Client, query: str) -> str | None:
        """Search Wikimedia Commons for image files directly."""
        search_resp = http.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "list": "search",
                "srsearch": query, "srnamespace": 6,
                "srlimit": 5, "format": "json",
            },
            headers=headers,
        )
        if not search_resp.is_success:
            return None
        hits = search_resp.json().get("query", {}).get("search", [])
        titles = [h["title"] for h in hits if h.get("title")]
        if not titles:
            return None
        info_resp = http.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "titles": "|".join(titles[:3]),
                "prop": "imageinfo",
                "iiprop": "url|mediatype",
                "iiurlwidth": 800,
                "format": "json",
            },
            headers=headers,
        )
        if not info_resp.is_success:
            return None
        for page in info_resp.json().get("query", {}).get("pages", {}).values():
            for info in page.get("imageinfo", []):
                if info.get("mediatype") == "BITMAP":
                    return info.get("thumburl") or info.get("url")
        return None

    try:
        with httpx.Client(timeout=20, follow_redirects=True) as http:
            # 1. Wikipedia page thumbnail
            ref_image_url, species_page_url = _wikipedia_thumb(http, plant.species)

            # 2. Wikimedia Commons file search
            if not ref_image_url:
                ref_image_url = _commons_search(http, plant.species)

            # 3. Retry with genus only
            if not ref_image_url and " " in plant.species:
                genus = plant.species.split()[0]
                ref_image_url, species_page_url = _wikipedia_thumb(http, genus)
                if not ref_image_url:
                    ref_image_url = _commons_search(http, genus)

            # Download and save locally
            local_ref_url = None
            if ref_image_url:
                img_resp = http.get(ref_image_url, headers=headers)
                img_resp.raise_for_status()
                content_type = img_resp.headers.get("content-type", "image/jpeg")
                ext = ".jpg" if "jpeg" in content_type else "." + content_type.split("/")[-1].split(";")[0]
                local_ref_url = _save_bytes(img_resp.content, ext)

    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Network error: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Image download failed: {exc.response.status_code}")

    # Move current photo to gallery slot before overwriting
    if plant.photo_url and not plant.user_photo_url:
        plant.user_photo_url = plant.photo_url

    if local_ref_url:
        plant.photo_url = local_ref_url
    if species_page_url:
        plant.wiki_url = species_page_url

    db.commit()
    db.refresh(plant)
    return plant


