"""Одинаковые правила ввода для консоли и REST API."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


class NoteData(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    body: Annotated[str, StringConstraints(max_length=4000)] = ""


class NoteView(NoteData):
    model_config = ConfigDict(from_attributes=True)

    id: int
