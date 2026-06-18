"""restore user photos as main photo_url

Revision ID: 007
Revises: 006
Create Date: 2026-06-18

Where user_photo_url exists (original user photo was displaced by reference image),
restore it as the main photo_url and clear user_photo_url.
"""
from typing import Union
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        UPDATE plants
        SET photo_url = user_photo_url,
            user_photo_url = NULL
        WHERE user_photo_url IS NOT NULL
    """)


def downgrade() -> None:
    pass
