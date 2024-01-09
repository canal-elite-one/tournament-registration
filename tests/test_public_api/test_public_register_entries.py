from conftest import BaseTest
from http import HTTPStatus
import pytest

from flaskr.api.db import get_player_not_found_error


overall_correct_licence = 722370
overall_incorrect_licence = 555555

correct_registration = (
    4526124,
    {"categoryIds": ["1"]},
    [
        {
            "categoryId": "B",
            "entryFee": 7,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-17T18:01:20",
            "markedAsPresent": True,
        },
        {
            "categoryId": "F",
            "entryFee": 7,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-25T21:56:50",
            "markedAsPresent": True,
        },
        {
            "categoryId": "1",
            "entryFee": 7,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-30T12:18:21",
            "markedAsPresent": False,
        },
    ],
)

correct_registration_with_duplicates = (
    4526124,
    {
        "categoryIds": ["1", "B", "F"],
    },
    [
        {
            "categoryId": "B",
            "entryFee": 7,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-17T18:01:20",
            "markedAsPresent": True,
        },
        {
            "categoryId": "F",
            "entryFee": 7,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-25T21:56:50",
            "markedAsPresent": True,
        },
        {
            "categoryId": "1",
            "entryFee": 7,
            "licenceNo": 4526124,
            "markedAsPaid": False,
            "registrationTime": "2023-11-30T12:18:21",
            "markedAsPresent": False,
        },
    ],
)

correct_register_entries = [
    correct_registration,
    correct_registration_with_duplicates,
]

incorrect_registration_color_violation = (
    7886249,
    {"categoryIds": ["1"]},
    {"error": "One or several potential entries violate color constraint."},
)

incorrect_registration_gender_points_violation = (
    4526124,
    {
        "categoryIds": ["A"],
    },
    {
        "error": "Tried to register some entries violating either gender or points "
        "conditions: ['A']",
    },
)

incorrect_registration_nonexisting_player = (
    overall_incorrect_licence,
    {"categoryIds": ["A"]},
    get_player_not_found_error(overall_incorrect_licence),
)

incorrect_registrations_missing_categoryids_json_fields = (
    4526124,
    {},
    {"error": {"categoryIds": ["Missing data for required field."]}},
)

incorrect_registration_empty_categories = (
    4526124,
    {"categoryIds": []},
    {"error": "No categories to register entries in were sent."},
)

incorrect_registration_nonexisting_categories = (
    4526124,
    {
        "categoryIds": ["A", "a"],
    },
    {
        "error": "No categories with the following categoryIds ['a'] exist in the "
        "database",
    },
)

incorrect_register_entries = [
    incorrect_registration_color_violation,
    incorrect_registration_gender_points_violation,
    incorrect_registration_nonexisting_player,
    incorrect_registrations_missing_categoryids_json_fields,
    incorrect_registration_empty_categories,
    incorrect_registration_nonexisting_categories,
]


class TestRegisterEntries(BaseTest):
    @pytest.mark.parametrize("licence_no,payload,response", correct_register_entries)
    def test_correct_register_entries(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        response,
    ):
        r = client.post(f"/api/public/entries/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.CREATED, r.json
        assert "registeredEntries" in r.json, r.json
        # TODO add correct test for response

    @pytest.mark.parametrize("licence_no,payload,error", incorrect_register_entries)
    def test_incorrect_register_entries(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        error,
    ):
        r = client.post(f"/api/public/entries/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json
