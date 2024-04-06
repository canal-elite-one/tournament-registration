import os
from datetime import datetime
from enum import StrEnum

from pytest import fixture
from sqlalchemy import text

import public
import admin
from shared.api.db import Session, execute_dbmate

SAMPLE_DATA_PATH = "./tests/sample_data/"


class SampleDates(StrEnum):
    BEFORE_START = "2021-01-01 00:00:00"
    BEFORE_CUTOFF = "2023-01-01 00:00:00"
    AFTER_CUTOFF = "2025-01-01 00:00:00"


config = {
    "TOURNAMENT_REGISTRATION_CUTOFF": datetime.fromisoformat("2024-01-01 00:00:00"),
    "TOURNAMENT_REGISTRATION_START": datetime.fromisoformat("2022-01-01 00:00:00"),
    "MAX_ENTRIES_PER_DAY": 2,
    "FFTT_API_URL": "http://fake_url",
    "FFTT_SERIAL_NO": "jfdqklmqoidufqids",
    "FFTT_APP_ID": "aezuiraop",
    "FFTT_PASSWORD": "aeuirpodisqfhqmkd",
}


def drop_presence_payment():
    with Session() as session:
        session.execute(
            text(
                "UPDATE entries "
                "SET marked_as_present=null "
                "WHERE marked_as_present=true;",
            ),
        )
        session.execute(text("UPDATE entries " "SET marked_as_paid=false;"))
        session.execute(text("UPDATE players " "SET total_actual_paid=0;"))
        session.commit()


class BaseTest:
    @fixture(scope="session")
    def public_app(self):
        app = public.create_app(debug=True)
        app.config.update(config)
        return app

    @fixture(scope="session")
    def admin_app(self):
        app = admin.create_app(debug=True)
        app.config.update(config)
        return app

    @fixture(scope="session")
    def public_client(self, public_app):
        return public_app.test_client()

    @fixture(scope="session")
    def admin_client(self, admin_app):
        return admin_app.test_client()

    @fixture
    def reset_db(self, request):
        execute_dbmate("up")

        def tear_down():
            with Session() as session:
                session.close_all()
            execute_dbmate("down")

        request.addfinalizer(tear_down)

    @fixture
    def populate(self):
        with Session() as session, open(
            os.path.join(SAMPLE_DATA_PATH, "categories.sql"),
        ) as categories_sql, open(
            os.path.join(SAMPLE_DATA_PATH, "players.sql"),
        ) as players_sql, open(
            os.path.join(SAMPLE_DATA_PATH, "entries.sql"),
        ) as entries_sql:
            session.execute(text(categories_sql.read()))
            session.execute(text(players_sql.read()))
            session.execute(text(entries_sql.read()))
            if datetime.now() < config["TOURNAMENT_REGISTRATION_CUTOFF"]:
                drop_presence_payment()
            session.commit()

    @fixture
    def set_a_few_bibs(self):
        with Session() as session:
            session.execute(
                text(
                    "UPDATE players SET bib_no = 1 WHERE licence_no = '722370';"
                    "UPDATE players SET bib_no = 2 WHERE licence_no = '5325506';",
                ),
            )
            session.commit()
