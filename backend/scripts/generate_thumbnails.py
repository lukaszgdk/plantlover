"""One-shot script: generate thumbnails for existing plant photos that don't have one."""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageOps
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.environ["DATABASE_URL"]
UPLOADS_DIR = Path(__file__).resolve().parents[1] / "uploads"

engine = create_engine(DATABASE_URL)


def make_thumbnail(content: bytes, max_px: int = 400) -> bytes:
    img = Image.open(io.BytesIO(content))
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75, optimize=True)
    return buf.getvalue()


with engine.connect() as conn:
    rows = conn.execute(
        text("SELECT id, photo_url FROM plants WHERE photo_url IS NOT NULL")
    ).fetchall()

    print(f"Found {len(rows)} plants needing thumbnails")

    for plant_id, photo_url in rows:
        if not photo_url.startswith("/uploads/"):
            print(f"  skip {plant_id}: external URL")
            continue

        photo_path = UPLOADS_DIR / Path(photo_url).name
        if not photo_path.exists():
            print(f"  skip {plant_id}: file not found ({photo_path.name})")
            continue

        try:
            content = photo_path.read_bytes()

            # Fix orientation in original
            img = Image.open(io.BytesIO(content))
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=92, optimize=True)
            fixed = buf.getvalue()
            photo_path.write_bytes(fixed)

            thumb = make_thumbnail(fixed)
            stem = photo_path.stem
            thumb_path = UPLOADS_DIR / f"{stem}_t.jpg"
            thumb_path.write_bytes(thumb)
            thumb_url = f"/uploads/{stem}_t.jpg"

            conn.execute(
                text("UPDATE plants SET photo_thumbnail_url = :thumb WHERE id = :id"),
                {"thumb": thumb_url, "id": plant_id},
            )
            orig_kb = len(content) // 1024
            thumb_kb = len(thumb) // 1024
            print(f"  ✓ {plant_id}: {orig_kb}KB → {thumb_kb}KB (orientation fixed)")
        except Exception as e:
            print(f"  ✗ {plant_id}: {e}")

    conn.commit()
    print("Done.")
