"""Вторая версия схемы: текст заметки с пустым значением для старых строк."""

from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"


def upgrade() -> None:
    op.add_column("notes", sa.Column("body", sa.Text, nullable=False, server_default=""))


def downgrade() -> None:
    with op.batch_alter_table("notes") as batch:
        batch.drop_column("body")
