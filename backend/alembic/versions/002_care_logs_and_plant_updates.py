"""care_logs table and plant column updates

Revision ID: 002
Revises: 001
Create Date: 2026-06-17
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op


def _id_type(is_pg: bool):
    if is_pg:
        from sqlalchemy.dialects.postgresql import UUID
        return UUID(as_uuid=True)
    return sa.String(36)

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    is_pg = op.get_bind().dialect.name == "postgresql"

    op.add_column("plants", sa.Column("common_name", sa.String(255), nullable=True))
    op.add_column("plants", sa.Column("next_watering", sa.DateTime(timezone=True), nullable=True))
    if is_pg:
        op.alter_column(
            "plants",
            "last_watered",
            type_=sa.DateTime(timezone=True),
            postgresql_using="last_watered::timestamp with time zone",
            existing_nullable=True,
        )

    id_type = UUID(as_uuid=True) if is_pg else sa.String(36)
    op.create_table(
        "care_logs",
        sa.Column("id", id_type, primary_key=True),
        sa.Column(
            "plant_id",
            id_type,
            sa.ForeignKey("plants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "logged_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
    )
    op.create_index("ix_care_logs_plant_id", "care_logs", ["plant_id"])


def downgrade() -> None:
    op.drop_table("care_logs")
    if op.get_bind().dialect.name == "postgresql":
        op.alter_column(
            "plants",
            "last_watered",
            type_=sa.Date,
            postgresql_using="last_watered::date",
            existing_nullable=True,
        )
    op.drop_column("plants", "next_watering")
    op.drop_column("plants", "common_name")
