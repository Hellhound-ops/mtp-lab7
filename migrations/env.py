"""Точка входа Alembic, использующая то же подключение, что и приложение."""

from alembic import context

from database import Base, database_path, open_engine


if context.is_offline_mode():
    raise RuntimeError("Для миграции SQLite требуется подключение к файлу базы")

path = context.config.attributes.get("db_path") or database_path()
engine = open_engine(path)
try:
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()
finally:
    engine.dispose()
