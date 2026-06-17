"""care_logs table and plant column updates

Revision ID: 002
Revises: 001
Create Date: 2026-06-17
"""
from typing import Sequence, Union
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("plants", sa.Column("common_name", sa.String(255), nullable=True))
    op.add_column("plants", sa.Column("next_watering", sa.DateTime(timezone=True), nullable=True))
    op.alter_column(
        "plants",
        "last_watered",
        type_=sa.DateTime(timezone=True),
        postgresql_using="last_watered::timestamp with time zone",
        existing_nullable=True,
    )

    op.create_table(
        "care_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "plant_id",
            UUID(as_uuid=True),
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
    op.alter_column(
        "plants",
        "last_watered",
        type_=sa.Date,
        postgresql_using="last_watered::date",
        existing_nullable=True,
    )
    op.drop_column("plants", "next_watering")
    op.drop_column("plants", "common_name")
