from apis.shared.db import Session


def get_rw_session():
    with Session() as session, session.begin():
        yield session


def get_ro_session():
    with Session() as session:
        yield session
