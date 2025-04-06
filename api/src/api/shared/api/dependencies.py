import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = os.environ["DATABASE_URL"]

engine = create_engine(db_url)
GenSession = sessionmaker(engine)


def get_rw_session():
    with GenSession() as session, session.begin():
        yield session
        # try:
        #     yield session
        #     session.commit()
        # except Exception:
        #     session.rollback()
        #     raise


def get_ro_session():
    with GenSession() as session:
        yield session
