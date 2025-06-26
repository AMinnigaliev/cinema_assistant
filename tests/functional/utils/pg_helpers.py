from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from settings import config


def make_pg_engine() -> Engine:
    """
    Синхронный движок SQLAlchemy для PostgreSQL.
    """
    url = (
        f"postgresql://"
        f"{config.postgres_user}:{config.postgres_password}@"
        f"{config.postgres_host}:{config.postgres_port}/"
        f"{config.postgres_db}"
    )
    engine = create_engine(url, echo=True)

    return engine


def remove_user_db(login: str, pg_engine: Engine):
    """Удаляет пользователя login_test"""
    with pg_engine.connect() as conn:
        conn.execute(
            text("DELETE FROM auth.users WHERE login = :login"),
            {"login": login},
        )
        conn.commit()
