"""Подключение к SQLite, модель и операции над заметками."""

import csv
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import String, Text, URL, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(Text, server_default=text("''"))


def database_path() -> Path:
    return Path(os.getenv("MTP_LAB7_DB", "lab7.sqlite3")).resolve()


def open_engine(path: Path):
    return create_engine(URL.create("sqlite+pysqlite", database=str(path.resolve())))


def migration_config(path: Path) -> Config:
    config = Config(str(Path(__file__).with_name("alembic.ini")))
    config.attributes["db_path"] = path
    return config


def upgrade_database(path: Path) -> None:
    command.upgrade(migration_config(path), "head")


def list_notes(db: Session) -> list[Note]:
    return list(db.scalars(select(Note).order_by(Note.id)))


def delete_note(db: Session, note_id: int) -> bool:
    note = db.get(Note, note_id)
    if note is None:
        return False
    db.delete(note)
    return True


def export_notes(db: Session, destination: Path) -> int:
    notes = list_notes(db)
    with destination.open("x", encoding="utf-8-sig", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(("id", "title", "body"))
        writer.writerows((note.id, note.title, note.body) for note in notes)
    return len(notes)
