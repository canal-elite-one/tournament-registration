from conftest import BaseTest
from http import HTTPStatus
import pytest

from flaskr.api.db import get_player_not_found_error


overall_incorrect_licence = 5555555

correct_admin_assign_one = 9311764
correct_assign_one_response = {
    "bibNo": 3,
    "club": "BOURGETIN CTT",
    "email": "jfwxtzrmij@wnspze.com",
    "firstName": "Feitzmx",
    "gender": "F",
    "lastName": "ABJNNQES",
    "licenceNo": 9311764,
    "nbPoints": 1287,
    "totalActualPaid": 0,
    "phone": "+336983296275",
}

incorrect_admin_assign_one_without_any_assigned_error = {
    "error": "Cannot assign bib numbers manually before having assigned them in bulk",
}

incorrect_admin_assign_one_nonexisting_player = (
    overall_incorrect_licence,
    get_player_not_found_error(overall_incorrect_licence),
    HTTPStatus.BAD_REQUEST,
)

incorrect_admin_assign_one_already_assigned = (
    722370,
    {"error": "This player already has a bib assigned."},
    HTTPStatus.CONFLICT,
)

incorrect_admin_assign_one = [
    incorrect_admin_assign_one_already_assigned,
    incorrect_admin_assign_one_nonexisting_player,
]


class TestAPIAssignOneBibNo(BaseTest):
    def test_correct_assign_one(self, client, reset_db, populate, set_a_few_bibs):
        r = client.put(f"/api/admin/bibs/{correct_admin_assign_one}")
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == correct_assign_one_response, r.json

    def test_incorrect_assign_one_without_any_assigned(
        self,
        client,
        reset_db,
        populate,
    ):
        r = client.put(f"/api/admin/bibs/{correct_admin_assign_one}")
        assert r.status_code == HTTPStatus.CONFLICT, r.json
        assert r.json == incorrect_admin_assign_one_without_any_assigned_error, r.json

    @pytest.mark.parametrize(
        "licence_no,error,status_code",
        incorrect_admin_assign_one,
    )
    def test_incorrect_assign_one(
        self,
        client,
        reset_db,
        populate,
        set_a_few_bibs,
        licence_no,
        error,
        status_code,
    ):
        r = client.put(f"/api/admin/bibs/{licence_no}")
        assert r.status_code == status_code, r.json
        assert r.json == error, r.json
