# Лабораторная работа №7 — работа с СУБД

Бодров Георгий Александрович, группа 221341, вариант 3.
Методические указания, часть 1, страницы 13–14.

| Уровень | № | Задание | Реализация |
| --- | --- | --- | --- |
| Средний | 3 | Выбрать данные из таблицы | `python main.py list`, `database.list_notes` |
| Средний | 5 | Удалить запись | `python main.py delete ID`, `database.delete_note` |
| Средний | 9 | Экспорт данных в CSV | `python main.py export notes.csv` |
| Повышенный | 3 | Миграции Alembic | `alembic.ini`, `migrations/versions` |
| Повышенный | 7 | FastAPI + SQLAlchemy (REST) | `api.py`, `/notes` и `/notes/{id}` |

## Запуск

Нужен Python 3.12. Команды выполняются из папки проекта в PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
.\.venv\Scripts\python.exe main.py init
.\.venv\Scripts\python.exe main.py add 'Учебная заметка' --body 'Проверка SQLAlchemy'
.\.venv\Scripts\python.exe main.py list
.\.venv\Scripts\python.exe main.py export notes.csv
```

Укажите номер из вывода `list` в команде `python main.py delete ID`.
Экспорт использует UTF-8 с BOM и создаёт новый файл. При повторном экспорте
укажите другое имя. По умолчанию используется `lab7.sqlite3` в текущей папке.
Переменная `MTP_LAB7_DB` меняет путь для консоли, Alembic и API. Параметр `--db`
переопределяет путь только в консольной команде.

## Миграции Alembic

`0001` создаёт таблицу с идентификатором и заголовком. `0002` добавляет текст.
Существующие записи сохраняют идентификаторы и получают пустое поле текста.
Откат к `0001` убирает поле текста и сохраняет заголовки. Для демонстрации отката
создайте отдельную базу, поскольку при откате значения поля `body` удаляются.

```powershell
$env:MTP_LAB7_DB = 'migrations-demo.sqlite3'
.\.venv\Scripts\python.exe -m alembic upgrade 0001
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic downgrade 0001
.\.venv\Scripts\python.exe -m alembic upgrade head
Remove-Item Env:MTP_LAB7_DB
```

## REST API

```powershell
.\.venv\Scripts\python.exe main.py init
.\.venv\Scripts\python.exe -m uvicorn api:app
```

Откройте `http://127.0.0.1:8000/docs`. Через Swagger UI можно выполнить:

- `GET /notes` — список, `GET /notes/{id}` — запись по идентификатору.
- `POST /notes` — добавить `{"title": "Новая заметка", "body": "Текст"}`.
- `PUT /notes/{id}` — заменить заголовок и текст.
- `DELETE /notes/{id}` — удалить запись.

API и консоль используют один файл базы. Для отсутствующей записи API
возвращает `404`, при пустом заголовке — `422`.

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```
