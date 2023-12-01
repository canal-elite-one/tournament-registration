from pytest import fixture
from sqlalchemy import text

from flaskr import create_app
from flaskr.db import session, execute_dbmate

sample_data_path = "./tests/sample_data.sql"


class BaseTest:
    @fixture(scope="session")
    def app(self):
        execute_dbmate("down")
        return create_app()

    @fixture(scope='session')
    def client(self, app):
        return app.test_client()

    @fixture
    def reset_db(self, request):
        execute_dbmate("up")

        def tear_down():
            session.close_all()
            execute_dbmate("down")

        request.addfinalizer(tear_down)

    @fixture
    def populate(self):
        with open(sample_data_path) as sql:
            session.execute(text(sql.read()))
            session.commit()

