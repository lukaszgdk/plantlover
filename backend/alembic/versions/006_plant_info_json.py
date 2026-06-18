"""add plant_info json column

Revision ID: 006
Revises: 005
Create Date: 2026-06-18
"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("plants", sa.Column("plant_info", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("plants", "plant_info")
