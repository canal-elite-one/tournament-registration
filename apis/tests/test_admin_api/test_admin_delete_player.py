from http import HTTPStatus

import shared.api.api_errors as ae

from api.tests.conftest import BaseTest


overall_correct_licence = "722370"
overall_incorrect_licence = "5555555"

origin = "api_admin_delete_player"


class TestAPIDeletePlayer(BaseTest):
    def test_correct_admin_delete_player(self, admin_client, reset_db, populate):
        r = admin_client.delete(f"/api/admin/players/{overall_correct_licence}")
        assert r.status_code == HTTPStatus.NO_CONTENT, r.json

    def test_incorrect_admin_delete_player(
        self,
        admin_client,
        reset_db,
        populate,
    ):
        r = admin_client.delete(f"/api/admin/players/{overall_incorrect_licence}")
        error = ae.PlayerNotFoundError(
            origin=origin,
            licence_no=overall_incorrect_licence,
        )
        assert r.status_code == error.status_code, r.json
        assert r.json == error.to_dict(), r.json
