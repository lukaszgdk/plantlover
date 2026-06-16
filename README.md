# PlantLover

A full-stack plant management app. Track your plants, log care events, and identify species.

## Stack

- **Backend**: FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL
- **Frontend**: React 18 + Vite + TypeScript + React Router

## Quick Start

### 1. Start PostgreSQL

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure env
cp .env.example .env        # edit DATABASE_URL if needed

# Run migrations
export DATABASE_URL=postgresql://plantlover:plantlover@localhost:5432/plantlover
alembic upgrade head

# Start the API server
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### 3. Frontend

```bash
cd frontend

npm install
npm run dev
# → http://localhost:5173
```

## Project Structure

```
plantlover/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + CORS
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   ├── models.py        # ORM models
│   │   ├── schemas.py       # Pydantic v2 schemas
│   │   └── routers/
│   │       └── plants.py    # All /plants endpoints
│   ├── alembic/             # Migrations
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/plants.ts    # Typed fetch client
│       ├── types/plant.ts   # Shared TypeScript types
│       └── components/
│           ├── PlantList.tsx
│           ├── PlantCard.tsx
│           ├── PlantDetail.tsx
│           └── AddPlantForm.tsx
├── docker-compose.yml
└── .env.example
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /plants | List all plants |
| POST | /plants | Create a plant |
| GET | /plants/{id} | Get one plant |
| PUT | /plants/{id} | Update a plant |
| DELETE | /plants/{id} | Delete a plant |
| POST | /plants/{id}/identify | Identify species (mock) |
| POST | /plants/{id}/care-log | Log a care event |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |

## Extending

- **Real species identification**: Replace the mock in `routers/plants.py` (`identify_plant`) with a call to the Plant.id API or a vision model.
- **Auth**: Add FastAPI's `OAuth2PasswordBearer` and a `users` table.
- **Image uploads**: Add an `/upload` endpoint using `python-multipart` and store files in S3 or locally.
