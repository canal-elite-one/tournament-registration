from http import HTTPStatus

from freezegun import freeze_time
import pytest

import shared.api.api_errors as ae

from tests.conftest import BaseTest, before_cutoff, after_cutoff


overall_correct_licence = "722370"
overall_incorrect_licence = "5555555"
origin = "api_admin_delete_entries"

correct_delete_entries_all = (
    "722370",
    before_cutoff,
    {"categoryIds": ["A", "5", "7"]},
    {
        "bibNo": None,
        "club": "LE MANS SARTHE TENNIS DE TABLE",
        "email": "gzzduckcnh@kmgdxv.com",
        "firstName": "Dpwsaob",
        "gender": "F",
        "lastName": "ORHCWRNU",
        "licenceNo": "722370",
        "nbPoints": 689,
        "phone": "+336769763133",
        "registeredEntries": {},
    },
)

correct_delete_entries_partial = (
    "722370",
    before_cutoff,
    {"categoryIds": ["A", "5"]},
    {
        "bibNo": None,
        "club": "LE MANS SARTHE TENNIS DE TABLE",
        "email": "gzzduckcnh@kmgdxv.com",
        "firstName": "Dpwsaob",
        "gender": "F",
        "lastName": "ORHCWRNU",
        "licenceNo": "722370",
        "nbPoints": 689,
        "phone": "+336769763133",
        "registeredEntries": {
            "7": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": "722370",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 5,
                "registrationTime": "2023-09-17T05:10:51",
                "startTime": "2024-01-07T16:00:00",
            },
        },
    },
)

correct_delete_entries_after = (
    "722370",
    after_cutoff,
    {"categoryIds": ["A", "5"]},
    {
        "bibNo": None,
        "club": "LE MANS SARTHE TENNIS DE TABLE",
        "email": "gzzduckcnh@kmgdxv.com",
        "firstName": "Dpwsaob",
        "gender": "F",
        "lastName": "ORHCWRNU",
        "leftToPay": -3,
        "licenceNo": "722370",
        "nbPoints": 689,
        "paymentStatus": {
            "totalActualPaid": 3,
            "totalPaid": 0,
            "totalPresent": 0,
            "totalRegistered": 7,
        },
        "phone": "+336769763133",
        "registeredEntries": {
            "7": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": "722370",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 5,
                "registrationTime": "2023-09-17T05:10:51",
                "startTime": "2024-01-07T16:00:00",
            },
        },
    },
)

correct_admin_delete_entries = [
    correct_delete_entries_all,
    correct_delete_entries_partial,
    correct_delete_entries_after,
]

incorrect_delete_entries_missing_categories_json_field = (
    overall_correct_licence,
    {},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.DELETE_ENTRIES_FORMAT_MESSAGE,
        payload={"categoryIds": ["Missing data for required field."]},
    ),
)

incorrect_delete_entries_nonexisting_player = (
    overall_incorrect_licence,
    {"categoryIds": ["A", "5"]},
    ae.PlayerNotFoundError(
        origin=origin,
        licence_no=overall_incorrect_licence,
    ),
)

incorrect_delete_entries_invalid_categories = (
    "722370",
    {"categoryIds": ["P", "B", "5"]},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.INVALID_CATEGORY_ID_MESSAGES["deletion"],
        payload={"categoryIds": ["B", "P"]},
    ),
)

incorrect_admin_delete_entries = [
    incorrect_delete_entries_missing_categories_json_field,
    incorrect_delete_entries_nonexisting_player,
    incorrect_delete_entries_invalid_categories,
]


class TestAPIDeleteEntries(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,now,payload,response",
        correct_admin_delete_entries,
    )
    def test_correct_admin_delete_entries(
        self,
        admin_client,
        reset_db,
        populate,
        licence_no,
        now: str,
        payload,
        response,
    ):
        with freeze_time(now):
            r = admin_client.delete(f"/api/admin/entries/{licence_no}", json=payload)
            assert r.status_code == HTTPStatus.OK, r.json
            assert r.json == response, r.json

    @pytest.mark.parametrize(
        "licence_no,payload,error",
        incorrect_admin_delete_entries,
    )
    def test_incorrect_admin_delete_entries(
        self,
        admin_client,
        reset_db,
        populate,
        licence_no,
        payload,
        error,
    ):
        r = admin_client.delete(f"/api/admin/entries/{licence_no}", json=payload)
        assert r.status_code == error.status_code, r.json
        assert r.json == error.to_dict(), r.json
