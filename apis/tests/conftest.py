import os
from datetime import datetime
from enum import StrEnum
from pathlib import Path

from pytest import fixture
from sqlalchemy import text
from fastapi.testclient import TestClient

from apis import public, admin
from apis.shared.db import Session, empty_db

SAMPLE_DATA_PATH = Path(__file__).parent / "sample_data"


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
        session.execute(text("UPDATE entries SET marked_as_paid=false;"))
        session.execute(text("UPDATE players SET total_actual_paid=0;"))
        session.commit()


class BaseTest:
    @fixture(scope="session")
    def public_client(self):
        return TestClient(public.app)

    @fixture(scope="session")
    def admin_client(self):
        return TestClient(admin.app)

    @fixture
    def reset_db(self, request):
        empty_db()

        def tear_down():
            empty_db()

        request.addfinalizer(tear_down)

    @fixture
    def populate(self):
        with (
            Session() as session,
            open(
                os.path.join(SAMPLE_DATA_PATH, "categories.sql"),
            ) as categories_sql,
            open(
                os.path.join(SAMPLE_DATA_PATH, "players.sql"),
            ) as players_sql,
            open(
                os.path.join(SAMPLE_DATA_PATH, "entries.sql"),
            ) as entries_sql,
        ):
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
