"""ЛР №7, вариант 3: выборка, удаление, экспорт и миграции."""

import argparse
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import Note, database_path, delete_note, export_notes, list_notes
from database import open_engine, upgrade_database
from schemas import NoteData


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=database_path(), help="файл SQLite")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init", help="применить миграции Alembic")
    commands.add_parser("list", help="выбрать все записи")
    add = commands.add_parser("add", help="создать запись для демонстрации")
    add.add_argument("title")
    add.add_argument("--body", default="")
    delete = commands.add_parser("delete", help="удалить запись по id")
    delete.add_argument("id", type=int)
    export = commands.add_parser("export", help="экспортировать строки в новый CSV-файл")
    export.add_argument("destination", type=Path)
    args = parser.parse_args()

    try:
        if args.command == "init":
            upgrade_database(args.db)
            print(f"Миграции применены: {args.db}")
            return
        if not args.db.is_file():
            parser.error("Сначала создайте базу командой init")

        engine = open_engine(args.db)
        try:
            with Session(engine) as db:
                if args.command == "list":
                    for note in list_notes(db):
                        print(f"{note.id}. {note.title}: {note.body}")
                elif args.command == "add":
                    data = NoteData(title=args.title, body=args.body)
                    note = Note(**data.model_dump())
                    db.add(note)
                    db.flush()
                    note_id = note.id
                    db.commit()
                    print(f"Добавлена запись №{note_id}")
                elif args.command == "delete":
                    if not delete_note(db, args.id):
                        parser.error(f"Запись №{args.id} не найдена")
                    db.commit()
                    print(f"Удалена запись №{args.id}")
                elif args.command == "export":
                    count = export_notes(db, args.destination)
                    print(f"В {args.destination} экспортировано записей: {count}")
        finally:
            engine.dispose()
    except (OSError, SQLAlchemyError, ValidationError) as error:
        parser.exit(1, f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()
