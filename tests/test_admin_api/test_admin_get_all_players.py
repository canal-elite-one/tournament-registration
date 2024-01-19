from http import HTTPStatus
from json import loads

from freezegun import freeze_time
import pytest

from tests.conftest import BaseTest, before_cutoff, after_cutoff

with open("./tests/test_admin_api/all_players.json") as f:
    all_players_data = loads(f.read())

correct_admin_get_all_players = [
    (before_cutoff, all_players_data["before_cutoff"], False),
    (after_cutoff, all_players_data["after_cutoff"], False),
    (before_cutoff, all_players_data["before_cutoff_present_only"], True),
    (after_cutoff, all_players_data["after_cutoff_present_only"], True),
]


class TestAPIGetAllPlayers(BaseTest):
    @pytest.mark.parametrize("now,response,present_only", correct_admin_get_all_players)
    def test_admin_get_all_players(
        self,
        admin_client,
        reset_db,
        populate,
        now: str,
        response,
        present_only,
    ):
        present = "true" if present_only else "false"
        with freeze_time(now):
            r = admin_client.get(f"/api/admin/players/all?present_only={present}")
            assert r.status_code == HTTPStatus.OK, r.json
            assert r.json == response, r.json
