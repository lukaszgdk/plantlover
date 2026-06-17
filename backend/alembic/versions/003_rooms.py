"""add rooms table and room_id to plants

Revision ID: 003
Revises: 002
Create Date: 2026-06-17
"""
from typing import Sequence, Union
import uuid
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DEFAULT_ROOMS = [
    {"name": "Salon",        "icon": "🛋️"},
    {"name": "Sypialnia",    "icon": "🛏️"},
    {"name": "Kuchnia",      "icon": "🍳"},
    {"name": "Pokój dzieci", "icon": "🧸"},
    {"name": "Balkon",       "icon": "🌿"},
]


def upgrade() -> None:
    op.create_table(
        "rooms",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("icon", sa.String(32), nullable=True),
    )

    op.add_column("plants", sa.Column("room_id", UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_plants_room_id",
        "plants", "rooms",
        ["room_id"], ["id"],
        ondelete="SET NULL",
    )

    rooms_table = sa.table(
        "rooms",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("icon", sa.String),
    )
    op.bulk_insert(
        rooms_table,
        [{"id": uuid.uuid4(), "name": r["name"], "icon": r["icon"]} for r in _DEFAULT_ROOMS],
    )


def downgrade() -> None:
    op.drop_constraint("fk_plants_room_id", "plants", type_="foreignkey")
    op.drop_column("plants", "room_id")
    op.drop_table("rooms")
