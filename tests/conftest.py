import os

from pytest import fixture
from flaskr import create_app
import subprocess

from flaskr.db import session

migration_directory = "./flaskr/sql/migration"
sample_data_path = "./tests/sample_data.sql"


def execute_dbmate(command, database_url=None):
    subprocess.run(["dbmate", "-d", migration_directory, "--no-dump-schema"] + (["--url", database_url] if database_url
                                                                                else []) + [command], env=os.environ.copy(),)


class BaseTest:
    @fixture(scope="session")
    def app(self):
        return create_app()

    @fixture(scope='session')
    def client(self, app):
        return app.test_client()

    @fixture
    def reset_db(self, request):
        execute_dbmate("up", os.environ.get("DATABASE_URL"))

        def tear_down():
            session.close_all()
            execute_dbmate("down", os.environ.get("DATABASE_URL"))

        request.addfinalizer(tear_down)

    @fixture
    def populate(self):
        subprocess.run(["psql", os.environ.get("DATABASE_URL"), "-q", "-f", sample_data_path])
