import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routers import plants, rooms
from .routers import schedule as schedule_router

_missing = [v for v in ("DATABASE_URL", "PLANTNET_API_KEY") if not os.environ.get(v)]
if _missing:
    raise RuntimeError(f"Missing required environment variables: {', '.join(_missing)}")

app = FastAPI(title="PlantLover API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plants.router)
app.include_router(rooms.router)
app.include_router(schedule_router.router)

# Serve uploaded plant photos
_uploads_dir = Path(__file__).parent.parent / "uploads"
_uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads_dir), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok"}


FRONTEND_DIST = Path(__file__).parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    _assets_dir = FRONTEND_DIST / "assets"
    if _assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="static-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        return FileResponse(FRONTEND_DIST / "index.html")
