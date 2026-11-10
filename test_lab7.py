"""Интеграционные проверки миграций, базы, CSV и API."""

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from alembic import command
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from api import create_app
from database import export_notes, list_notes, migration_config, open_engine, upgrade_database


class LabTests(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "notes.sqlite3"
        self.engine = open_engine(self.path)
        self.addCleanup(self.engine.dispose)

    def test_migrate_existing_data(self):
        config = migration_config(self.path)
        command.upgrade(config, "0001")
        with self.engine.begin() as db:
            db.execute(text("INSERT INTO notes (title) VALUES ('Старая запись')"))
        upgrade_database(self.path)
        with Session(self.engine) as db:
            note = list_notes(db)[0]
            self.assertEqual((note.title, note.body), ("Старая запись", ""))
        command.downgrade(config, "0001")
        self.assertEqual([column["name"] for column in inspect(self.engine).get_columns("notes")], ["id", "title"])
        with self.engine.connect() as db:
            self.assertEqual(db.execute(text("SELECT title FROM notes")).scalar_one(), "Старая запись")
        upgrade_database(self.path)
        command.check(config)

    def test_api_and_export_share_database(self):
        upgrade_database(self.path)
        with TestClient(create_app(self.path)) as client:
            self.assertEqual(client.get("/notes").json(), [])
            self.assertEqual(client.post("/notes", json={"title": "  "}).status_code, 422)
            created = client.post("/notes", json={"title": " Заметка ", "body": "Первая строка\nВторая строка"})
            self.assertEqual(created.status_code, 201)
            note_id = created.json()["id"]
            endpoint = f"/notes/{note_id}"
            self.assertEqual(client.get(endpoint).json()["title"], "Заметка")
            destination = self.path.with_suffix(".csv")
            with Session(self.engine) as db:
                self.assertEqual(export_notes(db, destination), 1)
                with self.assertRaises(FileExistsError):
                    export_notes(db, destination)
            with destination.open(encoding="utf-8-sig", newline="") as source:
                self.assertEqual(next(csv.DictReader(source))["body"], "Первая строка\nВторая строка")
            self.assertEqual(client.put(endpoint, json={"title": "Обновлено"}).json()["title"], "Обновлено")
            self.assertEqual(client.delete(endpoint).status_code, 204)
            self.assertEqual(client.get(endpoint).status_code, 404)
            self.assertEqual(client.get("/notes").json(), [])
