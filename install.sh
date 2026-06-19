#!/bin/bash
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC}  $1"; }
die()  { echo -e "${RED}✗${NC} $1"; exit 1; }

echo "=== PlantLover installer ==="
echo ""

# --- Prerequisites ---
command -v python3 >/dev/null 2>&1 || die "Python 3 is required (https://python.org)"
command -v node    >/dev/null 2>&1 || die "Node.js 18+ is required (https://nodejs.org)"
command -v docker  >/dev/null 2>&1 || die "Docker is required (https://docs.docker.com/get-docker/)"
ok "Prerequisites found"

# --- PostgreSQL via Docker ---
echo ""
echo "Starting PostgreSQL..."
docker compose up -d db
echo "Waiting for PostgreSQL to be ready..."
until docker compose exec -T db pg_isready -U plantlover -q; do sleep 1; done
ok "PostgreSQL is ready"

# --- Backend ---
echo ""
echo "Setting up backend..."
cd backend

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt
ok "Backend dependencies installed"

if [ ! -f ".env" ]; then
  cp .env.example .env
  ok "Created backend/.env from .env.example"
else
  warn "backend/.env already exists, skipping"
fi

DATABASE_URL=postgresql://plantlover:plantlover@localhost:5432/plantlover \
  .venv/bin/alembic upgrade head
ok "Database migrations applied"

cd ..

# --- Frontend ---
echo ""
echo "Setting up frontend..."
cd frontend
npm install --silent
npm run build
ok "Frontend built"
cd ..

# --- Done ---
echo ""
echo -e "${GREEN}=== Installation complete ===${NC}"
echo ""
echo "To start the app:"
echo ""
echo "  Backend:"
echo "    cd backend"
echo "    DATABASE_URL=postgresql://plantlover:plantlover@localhost:5432/plantlover \\"
echo "      .venv/bin/uvicorn app.main:app --reload"
echo "    → http://localhost:8000"
echo ""
echo "  Frontend (dev):"
echo "    cd frontend && npm run dev"
echo "    → http://localhost:5173"
echo ""
echo "  Or serve the built frontend statically from frontend/dist/"
