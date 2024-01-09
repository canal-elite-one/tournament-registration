from conftest import BaseTest
from http import HTTPStatus
import pytest

from flaskr.api.db import get_player_not_found_error


overall_incorrect_licence = 5555555


correct_mark_unmark_present_nothing = (
    608834,
    {},
    {
        "bibNo": None,
        "club": "U S ETREPAGNY T T",
        "email": "wihnpztoim@tjbnck.com",
        "firstName": "Nxovesf",
        "gender": "F",
        "lastName": "GZLDPNEH",
        "licenceNo": 608834,
        "nbPoints": 1721,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 10,
            "totalRegistered": 24,
        },
        "phone": "+336044431914",
        "registeredEntries": {
            "3": {
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 1,
                "registrationTime": "2023-03-20T00:24:12",
            },
            "E": {
                "entryFee": 10,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 23,
                "registrationTime": "2023-11-02T18:50:24",
            },
            "G": {
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 24,
                "registrationTime": "2023-08-23T06:56:51",
            },
        },
    },
)

correct_mark_unmark_present = (
    608834,
    {
        "categoryIdsToMark": ["3"],
        "categoryIdsToUnmark": ["E"],
    },
    {
        "bibNo": None,
        "club": "U S ETREPAGNY T T",
        "email": "wihnpztoim@tjbnck.com",
        "firstName": "Nxovesf",
        "gender": "F",
        "lastName": "GZLDPNEH",
        "licenceNo": 608834,
        "nbPoints": 1721,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 7,
            "totalRegistered": 24,
        },
        "phone": "+336044431914",
        "registeredEntries": {
            "3": {
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 1,
                "registrationTime": "2023-03-20T00:24:12",
            },
            "E": {
                "entryFee": 10,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 23,
                "registrationTime": "2023-11-02T18:50:24",
            },
            "G": {
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 24,
                "registrationTime": "2023-08-23T06:56:51",
            },
        },
    },
)

correct_mark_unmark_present_idempotent = (
    608834,
    {
        "categoryIdsToMark": ["3", "E"],
    },
    {
        "bibNo": None,
        "club": "U S ETREPAGNY T T",
        "email": "wihnpztoim@tjbnck.com",
        "firstName": "Nxovesf",
        "gender": "F",
        "lastName": "GZLDPNEH",
        "licenceNo": 608834,
        "nbPoints": 1721,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 17,
            "totalRegistered": 24,
        },
        "phone": "+336044431914",
        "registeredEntries": {
            "3": {
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 1,
                "registrationTime": "2023-03-20T00:24:12",
            },
            "E": {
                "entryFee": 10,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 23,
                "registrationTime": "2023-11-02T18:50:24",
            },
            "G": {
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 24,
                "registrationTime": "2023-08-23T06:56:51",
            },
        },
    },
)

correct_admin_mark_present = [
    correct_mark_unmark_present_nothing,
    correct_mark_unmark_present,
    correct_mark_unmark_present_idempotent,
]

incorrect_mark_present_nonexisting_player = (
    overall_incorrect_licence,
    {},
    get_player_not_found_error(overall_incorrect_licence),
)

incorrect_mark_present_invalid_category = (
    7221154,
    {"categoryIdsToMark": ["AA", "A", "E"], "categoryIdsToUnmark": ["BB", "B", "E"]},
    {
        "error": "Tried to mark/unmark player for categories which he was not "
        "registered for or even non_existing catgories: ['A', 'AA', 'B', "
        "'BB']",
    },
)

incorrect_mark_present_mark_unmark_same_ids = (
    608834,
    {
        "categoryIdsToMark": ["E"],
        "categoryIdsToUnmark": ["E"],
    },
    {
        "error": "Tried to mark and unmark player as present for same categories: "
        "['E']",
    },
)

incorrect_admin_mark_present = [
    incorrect_mark_present_nonexisting_player,
    incorrect_mark_present_invalid_category,
    incorrect_mark_present_mark_unmark_same_ids,
]


class TestAPIMarkPresent(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,payload,response",
        correct_admin_mark_present,
    )
    def test_correct_admin_mark_present(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        response,
    ):
        r = client.put(f"/api/admin/present/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize(
        "licence_no,payload,error",
        incorrect_admin_mark_present,
    )
    def test_incorrect_admin_mark_present(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        error,
    ):
        r = client.put(f"/api/admin/present/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json
