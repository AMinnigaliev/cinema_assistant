import os
import importlib

from core.logger import logger
from database import clickhouse_session


def init_migration() -> None:
    with clickhouse_session.context_session() as session:
        session.raw("CREATE TABLE IF NOT EXISTS migration_log (name String) ENGINE = TinyLog")

        applied_migrations = {row.name for row in session.select("SELECT name FROM migration_log")}

        for file_name in sorted(os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrations'))):
            if not file_name.endswith('.py') or file_name == '__init__.py':
                continue

            if file_name in applied_migrations:
                continue

            module_name = f"migrations.{file_name[:-3]}"
            module = importlib.import_module(module_name)
            logger.info(f"Applying Clickhouse migration: {file_name}")
            module.migrate(session)
            session.raw(f"INSERT INTO migration_log (name) VALUES ('{file_name}')")


if __name__ == "__main__":
    init_migration()
