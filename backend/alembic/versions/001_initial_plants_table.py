"""initial plants table

Revision ID: 001
Revises:
Create Date: 2026-06-16
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op


def _id_type(is_pg: bool):
    if is_pg:
        from sqlalchemy.dialects.postgresql import UUID
        return UUID(as_uuid=True)
    return sa.String(36)

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    is_pg = op.get_bind().dialect.name == "postgresql"
    op.create_table(
        "plants",
        sa.Column("id", _id_type(is_pg), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("species", sa.String(255), nullable=True),
        sa.Column("photo_url", sa.String(1024), nullable=True),
        sa.Column("watering_interval_days", sa.Integer, nullable=True),
        sa.Column("last_watered", sa.Date, nullable=True),
        sa.Column("sunlight", sa.String(16), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("plants")
