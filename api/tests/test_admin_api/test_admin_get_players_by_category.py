import json
from http import HTTPStatus

from freezegun import freeze_time
import pytest

from api.tests.conftest import BaseTest, SampleDates


with open("./tests/test_admin_api/by_category.json") as f:
    by_category_data = json.loads(f.read())

correct_admin_get_players_by_category = [
    (SampleDates.BEFORE_CUTOFF, by_category_data["before_cutoff"], False),
    (SampleDates.AFTER_CUTOFF, by_category_data["after_cutoff"], False),
    (SampleDates.BEFORE_CUTOFF, by_category_data["before_cutoff_present_only"], True),
    (SampleDates.AFTER_CUTOFF, by_category_data["after_cutoff_present_only"], True),
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
