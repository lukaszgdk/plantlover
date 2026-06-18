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


@router.get("/ha-dashboard")
def ha_dashboard(db: Session = Depends(get_db)):
    import unicodedata, re
    from collections import defaultdict
    from fastapi.responses import PlainTextResponse

    def slugify(text: str) -> str:
        _pl = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
        text = text.translate(_pl)
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
        text = text.lower()
        text = re.sub(r"[^\w]+", "_", text)
        return text.strip("_")

    plants = db.query(PlantModel).order_by(PlantModel.name).all()

    # Grupuj po pokojach; rośliny bez pokoju trafiają do None
    by_room: dict = defaultdict(list)
    for p in plants:
        by_room[p.room].append(p)

    # Widoki per pokój
    room_views = []
    for room, room_plants in sorted(by_room.items(), key=lambda kv: kv[0].name if kv[0] else ""):
        room_name = room.name if room else "Bez pokoju"
        room_slug = slugify(room_name)
        room_button_slug = f"{room_slug}_podlej_wszystkie"

        # Licznik duplikatów w obrębie pokoju
        name_seen: dict = {}
        plant_cards = []
        for p in room_plants:
            prefix = f"{room_name} " if room else ""
            base = slugify(f"{prefix}{p.name}")
            name_seen[base] = name_seen.get(base, 0) + 1
            n = name_seen[base]
            suffix = f"_{n}" if n > 1 else ""

            plant_cards.append(f"""\
      - type: entities
        title: "{p.name}"
        entities:
          - entity: sensor.{base}_dni_do_podlania{suffix}
            name: Dni do podlania
          - entity: sensor.{base}_ostatnie_podlanie{suffix}
            name: Ostatnie podlanie
          - entity: button.{base}_podlej{suffix}
            name: 💧 Podlej""")

        # Zbierz entity_id przycisków podlania dla każdej rośliny w pokoju
        button_entities = []
        _seen2: dict = {}
        for p in room_plants:
            prefix = f"{room_name} " if room else ""
            b = slugify(f"{prefix}{p.name}")
            _seen2[b] = _seen2.get(b, 0) + 1
            suf = f"_{_seen2[b]}" if _seen2[b] > 1 else ""
            button_entities.append(f"button.{b}_podlej{suf}")
        all_buttons = "\n              - ".join(button_entities)

        cards_str = "\n\n".join(plant_cards)
        room_views.append(f"""\
  - title: "{room_name}"
    path: {room_slug}
    cards:

      - type: button
        name: "💧 Podlej wszystkie w {room_name}"
        icon: mdi:watering-can
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id:
              - {all_buttons}


{cards_str}""")

    views = "\n\n".join(room_views)
    yaml = f"title: 🌿 PlantLover\nviews:\n{views}\n"
    return PlainTextResponse(yaml, media_type="text/yaml")


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


@router.post("/{plant_id}/water")
def water_plant(plant_id: uuid.UUID, db: Session = Depends(get_db)):
    plant = get_plant_or_404(plant_id, db)
    now = datetime.now(tz=timezone.utc)
    plant.last_watered = now
    plant.next_watering = (
        now + timedelta(days=plant.watering_interval_days)
        if plant.watering_interval_days
        else None
    )
    from ..achievements import check_and_unlock
    newly_unlocked = check_and_unlock(db, plant, now)
    db.commit()
    db.refresh(plant)
    return {
        "plant_id": str(plant.id),
        "last_watered": plant.last_watered,
        "next_watering": plant.next_watering,
        "newly_unlocked": newly_unlocked,
    }


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

    newly_unlocked: list[str] = []
    if payload.action == "watered":
        from ..achievements import check_and_unlock
        newly_unlocked = check_and_unlock(db, plant, watered_at)

    db.commit()
    db.refresh(entry)

    result = entry.__dict__.copy()
    result["newly_unlocked"] = newly_unlocked
    return result


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


@router.post("/{plant_id}/fetch-info", response_model=Plant)
def fetch_info(plant_id: uuid.UUID, db: Session = Depends(get_db)):
    import json as json_mod
    import urllib.parse

    plant = get_plant_or_404(plant_id, db)
    if not plant.species:
        raise HTTPException(status_code=400, detail="Roślina nie ma ustawionego gatunku")

    ua = {"User-Agent": "PlantLover/1.0 (homelab; contact: veonlight@gmail.com)"}
    species = plant.species
    info: dict = {}

    with httpx.Client(timeout=15, follow_redirects=True) as http:

        # 1. GBIF — taksonomia + zasięg geograficzny (bez klucza)
        try:
            r = http.get("https://api.gbif.org/v1/species/match",
                         params={"name": species, "verbose": "false"}, headers=ua)
            g = r.json()
            if g.get("matchType") != "NONE":
                info["kingdom"] = g.get("kingdom")
                info["family"] = g.get("family")
                info["genus"] = g.get("genus")
                info["order"] = g.get("order")
                gbif_key = g.get("usageKey")
                if gbif_key:
                    dist_r = http.get(f"https://api.gbif.org/v1/species/{gbif_key}/distributions",
                                      params={"limit": 30}, headers=ua)
                    localities = [
                        d["locality"] for d in dist_r.json().get("results", [])
                        if d.get("locality") and d.get("establishmentMeans") in (None, "", "NATIVE")
                    ]
                    if localities:
                        info["native_regions"] = localities
        except Exception:
            pass

        # 2. Wikidata — nazwy zwyczajowe + sitelinks do Wikipedii (PL/EN)
        qid = None
        pl_wiki_title = None
        en_wiki_title = None
        try:
            search_r = http.get("https://www.wikidata.org/w/api.php", headers=ua, params={
                "action": "wbsearchentities", "search": species,
                "language": "en", "type": "item", "format": "json", "limit": 1,
            })
            results = search_r.json().get("search", [])
            if results:
                qid = results[0]["id"]
                # pobierz nazwy zwyczajowe + sitelinks jednym zapytaniem
                ent_r = http.get("https://www.wikidata.org/w/api.php", headers=ua, params={
                    "action": "wbgetentities", "ids": qid,
                    "props": "claims|sitelinks",
                    "sitefilter": "plwiki|enwiki",
                    "format": "json",
                })
                ent = ent_r.json()["entities"][qid]
                sitelinks = ent.get("sitelinks", {})
                pl_wiki_title = sitelinks.get("plwiki", {}).get("title")
                en_wiki_title = sitelinks.get("enwiki", {}).get("title")

                # nazwy zwyczajowe z P1843
                p1843 = ent.get("claims", {}).get("P1843", [])
                pl_names, en_names = [], []
                for claim in p1843:
                    sv = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
                    if isinstance(sv, dict):
                        lang, text = sv.get("language", ""), sv.get("text", "")
                        if lang == "pl":
                            pl_names.append(text)
                        elif lang == "en":
                            en_names.append(text)
                names = pl_names or en_names
                if names:
                    info["common_names"] = names
        except Exception:
            pass

        # 3. Wikipedia PL → EN — pełny artykuł przez MediaWiki API
        def _wiki_fetch(lang: str, title: str) -> dict | None:
            r = http.get(f"https://{lang}.wikipedia.org/w/api.php", headers=ua, params={
                "action": "query", "titles": title,
                "prop": "extracts|info", "explaintext": "true",
                "exsectionformat": "plain", "inprop": "url", "format": "json",
            })
            pages = r.json().get("query", {}).get("pages", {})
            page = list(pages.values())[0] if pages else {}
            if "missing" in page or not page.get("extract"):
                return None
            return page

        try:
            import re
            SKIP = {"przypisy", "bibliografia", "linki zewnętrzne", "references", "external links", "notes", "see also", "footnotes"}

            def _parse_page(page: dict, lang: str, source_label: str | None = None) -> dict:
                full_text = page.get("extract", "")
                parts = re.split(r'\n{2,}([^\n]+)\n', full_text)
                intro = parts[0].strip()
                sections = []
                i = 1
                while i + 1 < len(parts):
                    title_s, body = parts[i].strip(), parts[i + 1].strip()
                    if title_s and body and title_s.lower() not in SKIP:
                        sections.append({"title": title_s, "text": body})
                    i += 2
                result = {
                    "description": intro,
                    "sections": sections or None,
                    "wikipedia_url": page.get("fullurl"),
                    "polish_name": page.get("title") if lang == "pl" else None,
                    "source_label": source_label,
                }
                return {k: v for k, v in result.items() if v}

            def _wikidata_sitelinks(search_term: str) -> tuple[str | None, str | None, str | None]:
                sr = http.get("https://www.wikidata.org/w/api.php", headers=ua, params={
                    "action": "wbsearchentities", "search": search_term,
                    "language": "en", "type": "item", "format": "json", "limit": 1,
                })
                res = sr.json().get("search", [])
                if not res:
                    return None, None, None
                qid_ = res[0]["id"]
                er = http.get("https://www.wikidata.org/w/api.php", headers=ua, params={
                    "action": "wbgetentities", "ids": qid_,
                    "props": "sitelinks", "sitefilter": "plwiki|enwiki", "format": "json",
                })
                sl = er.json()["entities"][qid_].get("sitelinks", {})
                return qid_, sl.get("plwiki", {}).get("title"), sl.get("enwiki", {}).get("title")

            def _best_page(pl_title: str | None, en_title: str | None) -> tuple[dict | None, str]:
                if pl_title:
                    p = _wiki_fetch("pl", pl_title)
                    if p:
                        return p, "pl"
                if en_title:
                    p = _wiki_fetch("en", en_title)
                    if p:
                        return p, "en"
                return None, "pl"

            # A) dokładny gatunek
            page, lang_used = _best_page(pl_wiki_title, en_wiki_title)
            fallback_label = None

            # B) fallback: artykuł rodzaju (Chlorophytum, Ficus, ...)
            if not page:
                genus = species.split()[0]
                _, pl_g, en_g = _wikidata_sitelinks(genus)
                page, lang_used = _best_page(pl_g, en_g)
                if page:
                    fallback_label = f"Brak artykułu dla gatunku — pokazuję informacje o rodzaju {genus}"

            if page:
                parsed = _parse_page(page, lang_used, fallback_label)
                info.update(parsed)

        except Exception:
            pass

    if not info:
        raise HTTPException(status_code=404, detail="Nie znaleziono informacji o tym gatunku")

    info = {k: v for k, v in info.items() if v}
    plant.plant_info = json_mod.dumps(info, ensure_ascii=False)
    db.commit()
    db.refresh(plant)
    return plant




