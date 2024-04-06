from http import HTTPStatus

import pytest
from freezegun import freeze_time

import shared.api.api_errors as ae

from tests.conftest import BaseTest, SampleDates


overall_incorrect_licence = "5555555"
overall_correct_licence = "9311764"

origin = "api_admin_assign_one_bib"

correct_admin_assign_one = "9311764"
correct_assign_one_response = {
    "bibNo": 3,
    "club": "BOURGETIN CTT",
    "email": "jfwxtzrmij@wnspze.com",
    "firstName": "Feitzmx",
    "gender": "F",
    "lastName": "ABJNNQES",
    "licenceNo": "9311764",
    "nbPoints": 1287,
    "phone": "+336983296275",
    "totalActualPaid": 7,
}

incorrect_admin_assign_one_nonexisting_player = (
    overall_incorrect_licence,
    ae.PlayerNotFoundError(
        origin=origin,
        licence_no=overall_incorrect_licence,
    ),
)

incorrect_admin_assign_one_already_assigned = (
    "722370",
    ae.BibConflictError(
        origin=origin,
        error_message=ae.THIS_BIB_ALREADY_ASSIGNED_MESSAGE,
        payload={"bibNo": 1, "licenceNo": "722370"},
    ),
)

incorrect_admin_assign_one = [
    incorrect_admin_assign_one_already_assigned,
    incorrect_admin_assign_one_nonexisting_player,
]


class TestAPIAssignOneBibNo(BaseTest):
    def test_correct_assign_one(self, admin_client, reset_db, populate, set_a_few_bibs):
        with freeze_time(SampleDates.AFTER_CUTOFF):
            r = admin_client.put(f"/api/admin/bibs/{correct_admin_assign_one}")
            assert r.status_code == HTTPStatus.OK, r.json
            assert r.json == correct_assign_one_response, r.json

    def test_incorrect_assign_one_without_any_assigned(
        self,
        admin_client,
        reset_db,
        populate,
    ):
        error = ae.BibConflictError(
            origin=origin,
            error_message=ae.NO_BIBS_ASSIGNED_MESSAGE,
        )
        with freeze_time(SampleDates.AFTER_CUTOFF):
            r = admin_client.put(f"/api/admin/bibs/{overall_correct_licence}")
            assert r.status_code == error.status_code, r.json
            assert r.json == error.to_dict(), r.json

    def test_incorrect_assign_one_before_cutoff(
        self,
        admin_client,
        reset_db,
        populate,
        set_a_few_bibs,
    ):
        error = ae.RegistrationCutoffError(
            origin=origin,
            error_message=ae.RegistrationMessages.NOT_ENDED,
        )
        with freeze_time(SampleDates.BEFORE_CUTOFF):
            r = admin_client.put(f"/api/admin/bibs/{correct_admin_assign_one}")
            assert r.status_code == error.status_code, r.json
            assert r.json == error.to_dict(), r.json

    @pytest.mark.parametrize(
        "licence_no,error",
        incorrect_admin_assign_one,
    )
    def test_incorrect_assign_one(
        self,
        admin_client,
        reset_db,
        populate,
        set_a_few_bibs,
        licence_no,
        error,
    ):
        with freeze_time(SampleDates.AFTER_CUTOFF):
            r = admin_client.put(f"/api/admin/bibs/{licence_no}")
            assert r.status_code == error.status_code, r.json
            assert r.json == error.to_dict(), r.json
