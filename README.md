# PlantLover

A full-stack plant management app. Track your plants, log care events, and identify species.

## Stack

- **Backend**: FastAPI + SQLAlchemy 2 + Alembic + SQLite
- **Frontend**: React 18 + Vite + TypeScript + React Router

## Quick Start

### 1. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
DATABASE_URL=sqlite:////data/plantlover.db alembic upgrade head

# Start the API server
DATABASE_URL=sqlite:////data/plantlover.db uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs  (Swagger UI)
```

### 2. Frontend

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
└── .env.example
```

## Environment Variables

| Variable            | Description                                                      |
|---------------------|------------------------------------------------------------------|
| `DATABASE_URL`      | SQLite connection string, e.g. `sqlite:////data/plantlover.db`   |
| `PLANTNET_API_KEY`  | API key for plant identification (plantnet.org)                  |

## Updating

If you're running the standalone LXC template, use the built-in update script:

```bash
plantlover-update
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /plants | List all plants |
| POST | /plants | Create a plant |
| GET | /plants/{id} | Get one plant |
| PUT | /plants/{id} | Update a plant |
| DELETE | /plants/{id} | Delete a plant |
| POST | /plants/{id}/identify | Identify species |
| POST | /plants/{id}/care-log | Log a care event |
