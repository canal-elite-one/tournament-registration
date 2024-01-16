import json
from http import HTTPStatus

from freezegun import freeze_time
import pytest

from tests.conftest import BaseTest, before_cutoff, after_cutoff


with open("./tests/test_admin_api/by_category.json") as f:
    by_category_data = json.loads(f.read())

correct_admin_get_players_by_category = [
    (before_cutoff, by_category_data["before_cutoff"], False),
    (after_cutoff, by_category_data["after_cutoff"], False),
    (before_cutoff, by_category_data["before_cutoff_present_only"], True),
    (after_cutoff, by_category_data["after_cutoff_present_only"], True),
]


class TestAPIGetAllPlayers(BaseTest):
    @pytest.mark.parametrize(
        "now,response,present_only",
        correct_admin_get_players_by_category,
    )
    def test_admin_get_players_by_category(
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
            r = admin_client.get(f"/api/admin/by_category?present_only={present}")
            assert r.status_code == HTTPStatus.OK, r.json
            assert r.json == response, r.json
