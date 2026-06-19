"""rename Łazienka to Pokój dzieci, update seed list

Revision ID: 004
Revises: 003
Create Date: 2026-06-17
"""
from typing import Sequence, Union
import uuid
import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Desired final state of seeded rooms
_DESIRED = [
    {"name": "Salon",        "icon": "🛋️"},
    {"name": "Sypialnia",    "icon": "🛏️"},
    {"name": "Kuchnia",      "icon": "🍳"},
    {"name": "Pokój dzieci", "icon": "🧸"},
    {"name": "Balkon",       "icon": "🌿"},
]


def upgrade() -> None:
    conn = op.get_bind()

    # Rename Łazienka → Pokój dzieci (keeps any assigned plants intact)
    conn.execute(
        sa.text(
            "UPDATE rooms SET name = 'Pokój dzieci', icon = '🧸' "
            "WHERE name = 'Łazienka' AND icon = '🚿'"
        )
    )

    # Ensure every desired room exists (idempotent — skip if already present)
    for room in _DESIRED:
        exists = conn.execute(
            sa.text("SELECT 1 FROM rooms WHERE name = :name LIMIT 1"),
            {"name": room["name"]},
        ).fetchone()
        if not exists:
            conn.execute(
                sa.text("INSERT INTO rooms (id, name, icon) VALUES (:id, :name, :icon)"),
                {"id": str(uuid.uuid4()), "name": room["name"], "icon": room["icon"]},
            )


def downgrade() -> None:
    # Restore Łazienka (only if Pokój dzieci still has no plants)
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE rooms SET name = 'Łazienka', icon = '🚿' "
            "WHERE name = 'Pokój dzieci' AND icon = '🧸' "
            "AND NOT EXISTS (SELECT 1 FROM plants WHERE room_id = rooms.id)"
        )
    )
