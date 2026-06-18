"""photo thumbnails

Revision ID: 009
Revises: 008
Create Date: 2026-06-18
"""
from alembic import op
import sqlalchemy as sa

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("plants", sa.Column("photo_thumbnail_url", sa.String(1024), nullable=True))


def downgrade():
    op.drop_column("plants", "photo_thumbnail_url")
