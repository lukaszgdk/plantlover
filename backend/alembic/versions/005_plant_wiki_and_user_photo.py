"""add user_photo_url and wiki_url to plants

Revision ID: 005
Revises: 004
Create Date: 2026-06-18
"""
from typing import Union
from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("plants", sa.Column("user_photo_url", sa.String(1024), nullable=True))
    op.add_column("plants", sa.Column("wiki_url", sa.String(1024), nullable=True))


def downgrade() -> None:
    op.drop_column("plants", "wiki_url")
    op.drop_column("plants", "user_photo_url")
