from conftest import BaseTest
from http import HTTPStatus
import pytest

from flaskr.api.db import get_player_not_found_error

overall_incorrect_licence = 9999999

correct_payment_pay_all = (
    4526124,
    {"categoryIds": ["B", "F"], "totalActualPaid": 14},
    {
        "bibNo": None,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "licenceNo": 4526124,
        "nbPoints": 1149,
        "paymentStatus": {
            "totalActualPaid": 14,
            "totalPaid": 14,
            "totalPresent": 14,
            "totalRegistered": 14,
        },
        "phone": "+336919756238",
        "registeredEntries": {
            "B": {
                "entryFee": 7,
                "licenceNo": 4526124,
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 44,
                "registrationTime": "2023-11-17T18:01:20",
            },
            "F": {
                "entryFee": 7,
                "licenceNo": 4526124,
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 34,
                "registrationTime": "2023-11-25T21:56:50",
            },
        },
    },
)

correct_payment_pay_partial = (
    4526124,
    {"categoryIds": ["B"], "totalActualPaid": 7},
    {
        "bibNo": None,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "licenceNo": 4526124,
        "nbPoints": 1149,
        "paymentStatus": {
            "totalActualPaid": 7,
            "totalPaid": 7,
            "totalPresent": 14,
            "totalRegistered": 14,
        },
        "phone": "+336919756238",
        "registeredEntries": {
            "B": {
                "entryFee": 7,
                "licenceNo": 4526124,
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 44,
                "registrationTime": "2023-11-17T18:01:20",
            },
            "F": {
                "entryFee": 7,
                "licenceNo": 4526124,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 34,
                "registrationTime": "2023-11-25T21:56:50",
            },
        },
    },
)

correct_payment_idempotent = (
    5326002,
    {"categoryIds": ["B"], "totalActualPaid": 7},
    {
        "bibNo": None,
        "club": "ERNEENNE Sport Tennis de Table",
        "email": "zvsbcnurlb@ieppes.com",
        "firstName": "Hoyhjni",
        "gender": "M",
        "lastName": "JTFLCUZD",
        "licenceNo": 5326002,
        "nbPoints": 1364,
        "paymentStatus": {
            "totalActualPaid": 7,
            "totalPaid": 7,
            "totalPresent": 14,
            "totalRegistered": 14,
        },
        "phone": "+336368307553",
        "registeredEntries": {
            "B": {
                "entryFee": 7,
                "licenceNo": 5326002,
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 32,
                "registrationTime": "2023-09-19T15:04:30",
            },
            "G": {
                "entryFee": 7,
                "licenceNo": 5326002,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 45,
                "registrationTime": "2023-11-16T12:30:04",
            },
        },
    },
)

correct_payment_nondefault_actual = (
    4526124,
    {"categoryIds": ["B"], "totalActualPaid": 6},
    {
        "bibNo": None,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "licenceNo": 4526124,
        "nbPoints": 1149,
        "paymentStatus": {
            "totalActualPaid": 6,
            "totalPaid": 7,
            "totalPresent": 14,
            "totalRegistered": 14,
        },
        "phone": "+336919756238",
        "registeredEntries": {
            "B": {
                "entryFee": 7,
                "licenceNo": 4526124,
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 44,
                "registrationTime": "2023-11-17T18:01:20",
            },
            "F": {
                "entryFee": 7,
                "licenceNo": 4526124,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 34,
                "registrationTime": "2023-11-25T21:56:50",
            },
        },
    },
)

correct_admin_make_payment = [
    correct_payment_pay_all,
    correct_payment_pay_partial,
    correct_payment_idempotent,
    correct_payment_nondefault_actual,
]

incorrect_payment_missing_json_fields = (
    5326002,
    {},
    {
        "error": {
            "categoryIds": ["Missing data for required field."],
            "totalActualPaid": ["Missing data for required field."],
        },
    },
)

incorrect_payment_misformatted_payload = (
    5326002,
    {"categoryIds": "B", "totalActualPaid": "a"},
    {
        "error": {
            "categoryIds": ["Not a valid list."],
            "totalActualPaid": ["Not a valid integer."],
        },
    },
)

incorrect_payment_misformatted_payload_2 = (
    5326002,
    {"categoryIds": [[]], "totalActualPaid": -1},
    {
        "error": {
            "categoryIds": {"0": ["Not a valid string."]},
            "totalActualPaid": ["Must be greater than or equal to 0."],
        },
    },
)

incorrect_payment_nonexisting_player = (
    overall_incorrect_licence,
    {"categoryIds": ["A"], "totalActualPaid": 7},
    get_player_not_found_error(overall_incorrect_licence),
)

incorrect_payment_invalid_categories = (
    7221154,
    {"categoryIds": ["AA", "A", "E", "G"], "totalActualPaid": 10},
    {
        "error": "Tried to pay the fee for some categories which either did not "
        "exist, the player was not registered for, or was not marked "
        "present: ['A', 'AA', 'E']",
    },
)

incorrect_payment_actual_payment_too_big = (
    4526124,
    {"categoryIds": ["B", "F"], "totalActualPaid": 15},
    {
        "error": "The 'totalActualPaid' field is higher than what the player must "
        "currently pay for all categories he is marked as present",
    },
)

incorrect_admin_make_payment = [
    incorrect_payment_missing_json_fields,
    incorrect_payment_misformatted_payload,
    incorrect_payment_misformatted_payload_2,
    incorrect_payment_nonexisting_player,
    incorrect_payment_invalid_categories,
    incorrect_payment_actual_payment_too_big,
]


class TestAPIMakePayment(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,payload,response",
        correct_admin_make_payment,
    )
    def test_correct_admin_make_payment(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        response,
    ):
        r = client.put(f"/api/admin/pay/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize(
        "licence_no,payload,error",
        incorrect_admin_make_payment,
    )
    def test_incorrect_admin_make_payment(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        error,
    ):
        r = client.put(f"/api/admin/pay/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json
