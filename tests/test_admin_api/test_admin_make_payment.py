from http import HTTPStatus

from freezegun import freeze_time
import pytest

import shared.api.api_errors as ae

from tests.conftest import BaseTest, before_cutoff, after_cutoff

overall_incorrect_licence = "9999999"
origin = "api_admin_make_payment"

correct_payment_pay_all = (
    "7219370",
    after_cutoff,
    {"categoryIds": ["2", "B", "F"], "totalActualPaid": 21},
    {
        "bibNo": None,
        "club": "LE MANS SARTHE TENNIS DE TABLE",
        "email": "ridjfnxjge@vdoxwg.com",
        "firstName": "Qqunjol",
        "gender": "F",
        "lastName": "CHYTWBCJ",
        "leftToPay": 0,
        "licenceNo": "7219370",
        "nbPoints": 1103,
        "paymentStatus": {
            "totalActualPaid": 21,
            "totalPaid": 21,
            "totalPresent": 21,
            "totalRegistered": 21,
        },
        "phone": "+336177732321",
        "registeredEntries": {
            "2": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": "7219370",
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 9,
                "registrationTime": "2023-06-26T09:48:53",
                "startTime": "2024-01-07T10:15:00",
            },
            "B": {
                "alternateName": "< 1500",
                "entryFee": 7,
                "licenceNo": "7219370",
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 44,
                "registrationTime": "2023-11-26T14:56:45",
                "startTime": "2024-01-06T10:15:00",
            },
            "F": {
                "alternateName": "Pas open féminin",
                "entryFee": 7,
                "licenceNo": "7219370",
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 22,
                "registrationTime": "2023-09-17T22:43:30",
                "startTime": "2024-01-06T15:00:00",
            },
        },
    },
)

correct_payment_pay_partial = (
    "7219370",
    after_cutoff,
    {"categoryIds": ["B"], "totalActualPaid": 7},
    {
        "bibNo": None,
        "club": "LE MANS SARTHE TENNIS DE TABLE",
        "email": "ridjfnxjge@vdoxwg.com",
        "firstName": "Qqunjol",
        "gender": "F",
        "lastName": "CHYTWBCJ",
        "leftToPay": 14,
        "licenceNo": "7219370",
        "nbPoints": 1103,
        "paymentStatus": {
            "totalActualPaid": 7,
            "totalPaid": 7,
            "totalPresent": 21,
            "totalRegistered": 21,
        },
        "phone": "+336177732321",
        "registeredEntries": {
            "2": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": "7219370",
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 9,
                "registrationTime": "2023-06-26T09:48:53",
                "startTime": "2024-01-07T10:15:00",
            },
            "B": {
                "alternateName": "< 1500",
                "entryFee": 7,
                "licenceNo": "7219370",
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 44,
                "registrationTime": "2023-11-26T14:56:45",
                "startTime": "2024-01-06T10:15:00",
            },
            "F": {
                "alternateName": "Pas open féminin",
                "entryFee": 7,
                "licenceNo": "7219370",
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 22,
                "registrationTime": "2023-09-17T22:43:30",
                "startTime": "2024-01-06T15:00:00",
            },
        },
    },
)

correct_payment_idempotent = (
    "7213526",
    after_cutoff,
    {"categoryIds": ["F"], "totalActualPaid": 7},
    {
        "bibNo": None,
        "club": "LE MANS VILLARET TT",
        "email": "eixivpskia@sdzloz.com",
        "firstName": "Fkwcbvs",
        "gender": "M",
        "lastName": "TYLANABF",
        "leftToPay": 0,
        "licenceNo": "7213526",
        "nbPoints": 1106,
        "paymentStatus": {
            "totalActualPaid": 7,
            "totalPaid": 7,
            "totalPresent": 7,
            "totalRegistered": 28,
        },
        "phone": "+336291515263",
        "registeredEntries": {
            "2": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": "7213526",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 4,
                "registrationTime": "2023-03-24T07:14:41",
                "startTime": "2024-01-07T10:15:00",
            },
            "6": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": "7213526",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 3,
                "registrationTime": "2023-05-15T21:10:54",
                "startTime": "2024-01-07T15:00:00",
            },
            "B": {
                "alternateName": "< 1500",
                "entryFee": 7,
                "licenceNo": "7213526",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 11,
                "registrationTime": "2023-05-03T04:45:23",
                "startTime": "2024-01-06T10:15:00",
            },
            "F": {
                "alternateName": "Pas open féminin",
                "entryFee": 7,
                "licenceNo": "7213526",
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 23,
                "registrationTime": "2023-09-21T07:22:44",
                "startTime": "2024-01-06T15:00:00",
            },
        },
    },
)

correct_payment_nondefault_actual = (
    "7219370",
    after_cutoff,
    {"categoryIds": ["B"], "totalActualPaid": 6},
    {
        "bibNo": None,
        "club": "LE MANS SARTHE TENNIS DE TABLE",
        "email": "ridjfnxjge@vdoxwg.com",
        "firstName": "Qqunjol",
        "gender": "F",
        "lastName": "CHYTWBCJ",
        "leftToPay": 15,
        "licenceNo": "7219370",
        "nbPoints": 1103,
        "paymentStatus": {
            "totalActualPaid": 6,
            "totalPaid": 7,
            "totalPresent": 21,
            "totalRegistered": 21,
        },
        "phone": "+336177732321",
        "registeredEntries": {
            "2": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": "7219370",
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 9,
                "registrationTime": "2023-06-26T09:48:53",
                "startTime": "2024-01-07T10:15:00",
            },
            "B": {
                "alternateName": "< 1500",
                "entryFee": 7,
                "licenceNo": "7219370",
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 44,
                "registrationTime": "2023-11-26T14:56:45",
                "startTime": "2024-01-06T10:15:00",
            },
            "F": {
                "alternateName": "Pas open féminin",
                "entryFee": 7,
                "licenceNo": "7219370",
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 22,
                "registrationTime": "2023-09-17T22:43:30",
                "startTime": "2024-01-06T15:00:00",
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
    "5326002",
    after_cutoff,
    {},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.PAYMENT_FORMAT_MESSAGE,
        payload={
            "categoryIds": ["Missing data for required field."],
            "totalActualPaid": ["Missing data for required field."],
        },
    ),
)

incorrect_payment_misformatted_payload = (
    "5326002",
    after_cutoff,
    {"categoryIds": "B", "totalActualPaid": "a"},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.PAYMENT_FORMAT_MESSAGE,
        payload={
            "categoryIds": ["Not a valid list."],
            "totalActualPaid": ["Not a valid integer."],
        },
    ),
)

incorrect_payment_misformatted_payload_2 = (
    "5326002",
    after_cutoff,
    {"categoryIds": [[]], "totalActualPaid": -1},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.PAYMENT_FORMAT_MESSAGE,
        payload={
            "categoryIds": {"0": ["Not a valid string."]},
            "totalActualPaid": ["Must be greater than or equal to 0."],
        },
    ),
)

incorrect_payment_nonexisting_player = (
    overall_incorrect_licence,
    after_cutoff,
    {"categoryIds": ["A"], "totalActualPaid": 7},
    ae.PlayerNotFoundError(origin=origin, licence_no=overall_incorrect_licence),
)

incorrect_payment_invalid_categories = (
    "7221154",
    after_cutoff,
    {"categoryIds": ["AA", "A", "E", "G"], "totalActualPaid": 10},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.INVALID_CATEGORY_ID_MESSAGES["payment"],
        payload={"categoryIds": ["A", "AA"]},
    ),
)

incorrect_payment_actual_payment_too_big = (
    "4526124",
    after_cutoff,
    {"categoryIds": ["B", "F"], "totalActualPaid": 15},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.ACTUAL_PAID_TOO_HIGH_MESSAGE,
        payload={"totalActualPaid": 15, "totalPresent": 14},
    ),
)

incorrect_payment_before_tournament = (
    "4526124",
    before_cutoff,
    {"categoryIds": ["B", "F"], "totalActualPaid": 14},
    ae.RegistrationCutoffError(
        origin=origin,
        error_message=ae.REGISTRATION_MESSAGES["not_ended"],
    ),
)

incorrect_admin_make_payment = [
    incorrect_payment_missing_json_fields,
    incorrect_payment_misformatted_payload,
    incorrect_payment_misformatted_payload_2,
    incorrect_payment_nonexisting_player,
    incorrect_payment_invalid_categories,
    incorrect_payment_actual_payment_too_big,
    incorrect_payment_before_tournament,
]


class TestAPIMakePayment(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,now,payload,response",
        correct_admin_make_payment,
    )
    def test_correct_admin_make_payment(
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
            r = admin_client.put(f"/api/admin/pay/{licence_no}", json=payload)
            assert r.status_code == HTTPStatus.OK, r.json
            assert r.json == response, r.json

    @pytest.mark.parametrize(
        "licence_no,now,payload,error",
        incorrect_admin_make_payment,
    )
    def test_incorrect_admin_make_payment(
        self,
        admin_client,
        reset_db,
        populate,
        licence_no,
        now: str,
        payload,
        error,
    ):
        with freeze_time(now):
            r = admin_client.put(f"/api/admin/pay/{licence_no}", json=payload)
            assert r.status_code == error.status_code, r.json
            assert r.json == error.to_dict(), r.json
