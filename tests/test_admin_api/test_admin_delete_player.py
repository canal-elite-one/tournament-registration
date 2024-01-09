from conftest import BaseTest
from http import HTTPStatus

from flaskr.api.db import get_player_not_found_error


overall_correct_licence = 722370
overall_incorrect_licence = 5555555


class TestAPIDeletePlayer(BaseTest):
    def test_correct_admin_delete_player(self, client, reset_db, populate):
        r = client.delete(f"/api/admin/players/{overall_correct_licence}")
        assert r.status_code == HTTPStatus.NO_CONTENT, r.json

    def test_incorrect_admin_delete_player(
        self,
        client,
        reset_db,
        populate,
    ):
        r = client.delete(f"/api/admin/players/{overall_incorrect_licence}")
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == get_player_not_found_error(
            overall_incorrect_licence,
        ), r.json
