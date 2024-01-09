from pytest import fixture
from sqlalchemy import text

from flaskr import create_app
from flaskr.api.db import Session, execute_dbmate, app_info

SAMPLE_DATA_PATH = "./tests/sample_data/"


class BaseTest:
    @fixture(scope="session")
    def app(self):
        return create_app()

    @fixture(scope="session")
    def client(self, app):
        return app.test_client()

    @fixture
    def reset_db(self, request):
        execute_dbmate("up")
        _ = app_info.registration_cutoff
        del app_info.registration_cutoff

        def tear_down():
            with Session() as session:
                session.close_all()
            execute_dbmate("down")

        request.addfinalizer(tear_down)

    @fixture
    def populate(self):
        with Session() as session:
            with open(SAMPLE_DATA_PATH + "categories.sql") as categories_sql:
                session.execute(text(categories_sql.read()))
                session.commit()
            with open(SAMPLE_DATA_PATH + "players.sql") as players_sql:
                session.execute(text(players_sql.read()))
                session.commit()
            with open(SAMPLE_DATA_PATH + "entries.sql") as entries_sql:
                session.execute(text(entries_sql.read()))
                session.commit()

    @fixture
    def set_a_few_bibs(self):
        with Session() as session:
            session.execute(
                text(
                    "UPDATE players SET bib_no = 1 WHERE licence_no = 722370;"
                    "UPDATE players SET bib_no = 2 WHERE licence_no = 5325506;",
                ),
            )
            session.commit()
