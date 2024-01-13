from freezegun import freeze_time

from tests.conftest import BaseTest, before_cutoff, after_cutoff
from http import HTTPStatus
import pytest

import flaskr.api.api_errors as ae

overall_incorrect_licence = 5555555

origin = "api_admin_mark_present"

correct_mark_unmark_present_nothing = (
    4422906,
    after_cutoff,
    {},
    {
        "bibNo": None,
        "club": "PUTEAUX TT CSM",
        "email": "sxeltzeokc@jrdstd.com",
        "firstName": "Mzxyyfw",
        "gender": "F",
        "lastName": "ITMZMIPM",
        "leftToPay": 0,
        "licenceNo": 4422906,
        "nbPoints": 1310,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 0,
            "totalRegistered": 21,
        },
        "phone": "+336072282639",
        "registeredEntries": {
            "1": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": 4422906,
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 57,
                "registrationTime": "2023-06-14T23:36:12",
                "startTime": "2024-01-07T09:00:00",
            },
            "B": {
                "alternateName": "< 1500",
                "entryFee": 7,
                "licenceNo": 4422906,
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 5,
                "registrationTime": "2023-03-25T00:35:57",
                "startTime": "2024-01-06T10:15:00",
            },
            "G": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": 4422906,
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 11,
                "registrationTime": "2023-06-05T04:06:42",
                "startTime": "2024-01-06T16:00:00",
            },
        },
    },
)

correct_mark_unmark_present = (
    608834,
    after_cutoff,
    {
        "categoryIdsPresence": {
            "E": False,
            "3": None,
            "G": True,
        },
    },
    {
        "bibNo": None,
        "club": "U S ETREPAGNY T T",
        "email": "wihnpztoim@tjbnck.com",
        "firstName": "Nxovesf",
        "gender": "F",
        "lastName": "GZLDPNEH",
        "leftToPay": 0,
        "licenceNo": 608834,
        "nbPoints": 1721,
        "paymentStatus": {
            "totalActualPaid": 7,
            "totalPaid": 0,
            "totalPresent": 7,
            "totalRegistered": 24,
        },
        "phone": "+336044431914",
        "registeredEntries": {
            "3": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 2,
                "registrationTime": "2023-03-20T00:24:12",
                "startTime": "2024-01-07T11:30:00",
            },
            "E": {
                "alternateName": None,
                "entryFee": 10,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 36,
                "registrationTime": "2023-11-02T18:50:24",
                "startTime": "2024-01-06T14:00:00",
            },
            "G": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 23,
                "registrationTime": "2023-08-23T06:56:51",
                "startTime": "2024-01-06T16:00:00",
            },
        },
    },
)

correct_mark_unmark_present_idempotent = (
    608834,
    after_cutoff,
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
        "leftToPay": 0,
        "licenceNo": 608834,
        "nbPoints": 1721,
        "paymentStatus": {
            "totalActualPaid": 17,
            "totalPaid": 17,
            "totalPresent": 17,
            "totalRegistered": 24,
        },
        "phone": "+336044431914",
        "registeredEntries": {
            "3": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 2,
                "registrationTime": "2023-03-20T00:24:12",
                "startTime": "2024-01-07T11:30:00",
            },
            "E": {
                "alternateName": None,
                "entryFee": 10,
                "licenceNo": 608834,
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 36,
                "registrationTime": "2023-11-02T18:50:24",
                "startTime": "2024-01-06T14:00:00",
            },
            "G": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 23,
                "registrationTime": "2023-08-23T06:56:51",
                "startTime": "2024-01-06T16:00:00",
            },
        },
    },
)

correct_marked_absent_before = (
    608834,
    before_cutoff,
    {
        "categoryIdsPresence": {"G": False},
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
        "phone": "+336044431914",
        "registeredEntries": {
            "3": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 2,
                "registrationTime": "2023-03-20T00:24:12",
                "startTime": "2024-01-07T11:30:00",
            },
            "E": {
                "alternateName": None,
                "entryFee": 10,
                "licenceNo": 608834,
                "markedAsPaid": True,
                "markedAsPresent": True,
                "rank": 36,
                "registrationTime": "2023-11-02T18:50:24",
                "startTime": "2024-01-06T14:00:00",
            },
            "G": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": 608834,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 23,
                "registrationTime": "2023-08-23T06:56:51",
                "startTime": "2024-01-06T16:00:00",
            },
        },
    },
)

correct_admin_mark_present = [
    correct_mark_unmark_present_nothing,
    correct_mark_unmark_present,
    correct_mark_unmark_present_idempotent,
    correct_marked_absent_before,
]

incorrect_mark_present_nonexisting_player = (
    overall_incorrect_licence,
    after_cutoff,
    {},
    ae.PlayerNotFoundError(
        origin=origin,
        licence_no=overall_incorrect_licence,
    ),
)

incorrect_mark_present_invalid_category = (
    7221154,
    after_cutoff,
    {
        "categoryIdsPresence": {
            "AA": True,
            "A": True,
            "E": True,
            "BB": False,
            "B": False,
        },
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.INVALID_CATEGORY_ID_MESSAGES["present"],
        payload={"categoryIds": ["A", "AA", "B", "BB"]},
    ),
)

incorrect_mark_present_before = (
    7221154,
    before_cutoff,
    {
        "categoryIdsPresence": {
            "E": True,
        },
    },
    ae.RegistrationCutoffError(
        origin=origin,
        error_message=ae.REGISTRATION_MESSAGES["not_ended_mark_present"],
    ),
)

incorrect_admin_mark_present = [
    incorrect_mark_present_nonexisting_player,
    incorrect_mark_present_invalid_category,
    incorrect_mark_present_before,
]


class TestAPIMarkPresent(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,now,payload,response",
        correct_admin_mark_present,
    )
    def test_correct_admin_mark_present(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        now: str,
        payload,
        response,
    ):
        with freeze_time(now):
            r = client.put(f"/api/admin/present/{licence_no}", json=payload)
            assert r.status_code == HTTPStatus.OK, r.json
            assert r.json == response, r.json

    @pytest.mark.parametrize(
        "licence_no,now,payload,error",
        incorrect_admin_mark_present,
    )
    def test_incorrect_admin_mark_present(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        now: str,
        payload,
        error,
    ):
        with freeze_time(now):
            r = client.put(f"/api/admin/present/{licence_no}", json=payload)
            assert r.status_code == error.status_code, r.json
            assert r.json == error.to_dict(), r.json
