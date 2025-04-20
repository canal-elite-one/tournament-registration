from apis.shared.db import Session


def get_rw_session():
    with Session() as session, session.begin():
        yield session
        # try:
        #     yield session
        #     session.commit()
        # except Exception:
        #     session.rollback()
        #     raise


def get_ro_session():
    with Session() as session:
        yield session
