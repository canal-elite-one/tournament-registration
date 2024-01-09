from conftest import BaseTest
from http import HTTPStatus
import pytest

from flaskr.api.db import get_player_not_found_error


overall_incorrect_licence = 5555555


correct_get_player_existing = (
    4526124,
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
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 14,
            "totalRegistered": 14,
        },
        "phone": "+336919756238",
        "registeredEntries": {
            "B": {
                "entryFee": 7,
                "licenceNo": 4526124,
                "markedAsPaid": False,
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

correct_get_player_late_registration = (
    9241901,
    {
        "bibNo": None,
        "club": "BOIS COLOMBES SPORTS",
        "email": "sobsfewmas@mmzbwc.com",
        "firstName": "Vtrgrdc",
        "gender": "M",
        "lastName": "ZBXLTMIV",
        "licenceNo": 9241901,
        "nbPoints": 1475,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 8,
            "totalRegistered": 29,
        },
        "phone": "+336535833023",
        "registeredEntries": {
            "1": {
                "entryFee": 8,
                "licenceNo": 9241901,
                "markedAsPaid": False,
                "markedAsPresent": True,
                "rank": 27,
                "registrationTime": "2024-11-08T22:03:59",
            },
            "3": {
                "entryFee": 7,
                "licenceNo": 9241901,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 6,
                "registrationTime": "2023-05-15T21:07:40",
            },
            "B": {
                "entryFee": 7,
                "licenceNo": 9241901,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 14,
                "registrationTime": "2023-05-17T21:17:58",
            },
            "G": {
                "entryFee": 7,
                "licenceNo": 9241901,
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 30,
                "registrationTime": "2023-09-15T23:55:16",
            },
        },
    },
)

correct_get_player = [
    correct_get_player_existing,
    correct_get_player_late_registration,
]

incorrect_get_player_nonexisting = (
    overall_incorrect_licence,
    False,
    get_player_not_found_error(overall_incorrect_licence),
)

incorrect_get_player_db_only = (
    7513006,
    True,
    get_player_not_found_error(7513006),
)

incorrect_get_player = [
    incorrect_get_player_nonexisting,
    incorrect_get_player_db_only,
]


class TestGetPlayer(BaseTest):
    @pytest.mark.parametrize("licence_no,response", correct_get_player)
    def test_correct_get_player(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        response,
    ):
        r = client.get(f"/api/public/players/{licence_no}")
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize("licence_no,db_only,error", incorrect_get_player)
    def test_incorrect_get_player(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        db_only,
        error,
    ):
        url = f"/api/public/players/{licence_no}"
        if db_only:
            url += "?db_only=true"
        r = client.get(url)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json
