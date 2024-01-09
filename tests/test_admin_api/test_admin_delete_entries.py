from conftest import BaseTest
from http import HTTPStatus
import pytest

from flaskr.api.db import get_player_not_found_error


overall_correct_licence = 722370
overall_incorrect_licence = 5555555

correct_delete_entries_all = (
    722370,
    {"categoryIds": ["A", "5", "7"]},
    {
        "bibNo": None,
        "club": "LE MANS SARTHE TENNIS DE TABLE",
        "email": "gzzduckcnh@kmgdxv.com",
        "firstName": "Dpwsaob",
        "gender": "F",
        "lastName": "ORHCWRNU",
        "licenceNo": 722370,
        "nbPoints": 689,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 0,
            "totalRegistered": 0,
        },
        "phone": "+336769763133",
        "registeredEntries": {},
    },
)

correct_delete_entries_partial = (
    722370,
    {"categoryIds": ["A", "5"]},
    {
        "bibNo": None,
        "club": "LE MANS SARTHE TENNIS DE TABLE",
        "email": "gzzduckcnh@kmgdxv.com",
        "firstName": "Dpwsaob",
        "gender": "F",
        "lastName": "ORHCWRNU",
        "licenceNo": 722370,
        "nbPoints": 689,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 0,
            "totalRegistered": 7,
        },
        "phone": "+336769763133",
        "registeredEntries": {
            "7": {
                "entryFee": 7,
                "licenceNo": 722370,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 5,
                "registrationTime": "2023-09-17T05:10:51",
            },
        },
    },
)

correct_admin_delete_entries = [
    correct_delete_entries_all,
    correct_delete_entries_partial,
]

incorrect_delete_entries_missing_categories_json_field = (
    overall_correct_licence,
    {},
    {"error": {"categoryIds": ["Missing data for required field."]}},
)

incorrect_delete_entries_nonexisting_player = (
    overall_incorrect_licence,
    {"categoryIds": ["A", "5"]},
    get_player_not_found_error(overall_incorrect_licence),
)

incorrect_delete_entries_invalid_categories = (
    722370,
    {"categoryIds": ["P", "B", "5"]},
    {
        "error": "Tried to delete some entries which were not registered or even for "
        "nonexisting categories: ['B', 'P'].",
    },
)

incorrect_admin_delete_entries = [
    incorrect_delete_entries_missing_categories_json_field,
    incorrect_delete_entries_nonexisting_player,
    incorrect_delete_entries_invalid_categories,
]


class TestAPIDeleteEntries(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,payload,response",
        correct_admin_delete_entries,
    )
    def test_correct_admin_delete_entries(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        response,
    ):
        r = client.delete(f"/api/admin/entries/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize(
        "licence_no,payload,error",
        incorrect_admin_delete_entries,
    )
    def test_incorrect_admin_delete_entries(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        error,
    ):
        r = client.delete(f"/api/admin/entries/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json
