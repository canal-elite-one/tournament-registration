from http import HTTPStatus
from json import loads

from freezegun import freeze_time
import pytest

from apis.public import BaseTest, SampleDates

with open("./tests/test_admin_api/all_players.json") as f:
    all_players_data = loads(f.read())

correct_admin_get_all_players = [
    (SampleDates.BEFORE_CUTOFF, all_players_data["before_cutoff"], False),
    (SampleDates.AFTER_CUTOFF, all_players_data["after_cutoff"], False),
    (SampleDates.BEFORE_CUTOFF, all_players_data["before_cutoff_present_only"], True),
    (SampleDates.AFTER_CUTOFF, all_players_data["after_cutoff_present_only"], True),
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
