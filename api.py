"""Повышенное №7: REST API FastAPI + SQLAlchemy."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy.orm import Session

from database import Note, database_path, delete_note, list_notes, open_engine
from schemas import NoteData, NoteView


def create_app(path: Path | None = None) -> FastAPI:
    engine = open_engine(path or database_path())

    @asynccontextmanager
    async def lifespan(_app):
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="МТП · ЛР №7 · Заметки", lifespan=lifespan)

    def session():
        with Session(engine) as db:
            yield db

    def get_note(db: Session, note_id: int) -> Note:
        note = db.get(Note, note_id)
        if note is None:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        return note

    @app.get("/notes", response_model=list[NoteView])
    def read_notes(db: Session = Depends(session)):
        return list_notes(db)

    @app.get("/notes/{note_id}", response_model=NoteView)
    def read_note(note_id: int, db: Session = Depends(session)):
        return get_note(db, note_id)

    @app.post("/notes", response_model=NoteView, status_code=201)
    def create_note(data: NoteData, db: Session = Depends(session)):
        note = Note(**data.model_dump())
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @app.put("/notes/{note_id}", response_model=NoteView)
    def update_note(note_id: int, data: NoteData, db: Session = Depends(session)):
        note = get_note(db, note_id)
        note.title = data.title
        note.body = data.body
        db.commit()
        db.refresh(note)
        return note

    @app.delete("/notes/{note_id}", status_code=204)
    def remove_note(note_id: int, db: Session = Depends(session)):
        if not delete_note(db, note_id):
            raise HTTPException(status_code=404, detail="Запись не найдена")
        db.commit()
        return Response(status_code=204)

    return app


app = create_app()
