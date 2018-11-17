import os
from contextlib import contextmanager

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

from alembic_scripts.utils import alembic_upgrade_head, alembic_downgrade_base

db_config = dict(
    address=os.environ.get("POSTGRES_HOST"),
    user=os.environ.get("POSTGRES_USER"),
    password=os.environ.get("POSTGRES_PASSWORD"),
    name=os.environ.get("POSTGRES_DB"),
    port=os.environ.get("POSTGRES_PORT"),
)

db_url = (
    f'postgresql+psycopg2://{db_config["user"]}:{db_config["password"]}@'
    f'{db_config["address"]}:{db_config["port"]}/{db_config["name"]}'
)

Base = declarative_base()
db_engine = create_engine(db_url, client_encoding='utf8')
DB_Session = orm.sessionmaker(bind=db_engine)
scoped_session = orm.scoped_session(DB_Session)


def recreate_postgres_metadata():
    create_db_if_not_exists()
    alembic_downgrade_base()
    alembic_upgrade_head()


def create_db_if_not_exists():
    if not database_exists(db_engine.url):
        create_database(db_engine.url)


@contextmanager
def get_db_session_scope():
    """Provide a transactional scope around a series of operations.
    """
    session = scoped_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
