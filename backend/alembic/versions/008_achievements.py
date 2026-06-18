"""achievements

Revision ID: 008
Revises: 007
Create Date: 2026-06-18
"""
from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "achievements",
        sa.Column("key", sa.String, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=False),
        sa.Column("icon", sa.String, nullable=False),
        sa.Column("condition_type", sa.String, nullable=False),
        sa.Column("condition_value", sa.Integer, nullable=False, server_default="1"),
    )

    op.create_table(
        "user_achievements",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("achievement_key", sa.String, sa.ForeignKey("achievements.key"), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("plant_id", sa.String, nullable=True),
    )

    # Seed achievement definitions
    op.execute("""
        INSERT INTO achievements (key, name, description, icon, condition_type, condition_value) VALUES
        ('first_watering',     'Pierwsze kroki',       'Podlej roślinę po raz pierwszy',                          '🌱', 'total_waterings', 1),
        ('watering_10',        'Pilny ogrodnik',       'Podlej rośliny łącznie 10 razy',                          '💧', 'total_waterings', 10),
        ('watering_50',        'Doświadczony',         'Podlej rośliny łącznie 50 razy',                          '🪣', 'total_waterings', 50),
        ('watering_100',       'Mistrz podlewania',    'Podlej rośliny łącznie 100 razy',                         '🏆', 'total_waterings', 100),
        ('on_time_5',          'Skrupulatny',          'Podlej roślinę na czas 5 razy z rzędu',                   '⏰', 'on_time_streak',  5),
        ('on_time_14',         'Niezawodny',           'Podlej roślinę na czas 14 razy z rzędu',                  '🎯', 'on_time_streak',  14),
        ('rescuer',            'Ratownik',             'Uratuj roślinę podlaną ponad 3 dni po terminie',          '🚑', 'late_rescue',     3),
        ('collector_5',        'Kolekcjoner',          'Miej jednocześnie 5 roślin',                              '🌿', 'plant_count',     5),
        ('collector_10',       'Botanik',              'Miej jednocześnie 10 roślin',                             '🌳', 'plant_count',     10),
        ('all_rooms',          'Zielony dom',          'Miej rośliny w co najmniej 3 różnych pokojach',           '🏠', 'room_count',      3),
        ('night_watering',     'Nocny ogrodnik',       'Podlej roślinę między 22:00 a 6:00',                      '🌙', 'night_watering',  1),
        ('week_streak',        'Tygodniowa passa',     'Podlewaj rośliny przez 7 dni z rzędu (min. 1 dziennie)',  '🔥', 'day_streak',      7),
        ('month_streak',       'Miesięczna passa',     'Podlewaj rośliny przez 30 dni z rzędu',                   '💎', 'day_streak',      30)
    """)


def downgrade():
    op.drop_table("user_achievements")
    op.drop_table("achievements")
