"""Первая версия схемы: таблица заметок с заголовком."""

from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None


def upgrade() -> None:
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(120), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("notes")
