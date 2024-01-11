from freezegun import freeze_time

from tests.conftest import BaseTest, before_cutoff, after_cutoff
import flaskr.api.api_errors as ae

from http import HTTPStatus

import pytest

origin = "api_admin_add_player"

correct_player_before = (
    {
        "licenceNo": 555555,
        "firstName": "Fjhgzg",
        "lastName": "MHIHOBB",
        "email": "dfqkjqpoe@aieop.com",
        "phone": "33489653754",
        "gender": "F",
        "nbPoints": 1500,
        "club": "USKB",
    },
    before_cutoff,
    {
        "bibNo": None,
        "club": "USKB",
        "email": "dfqkjqpoe@aieop.com",
        "firstName": "Fjhgzg",
        "gender": "F",
        "lastName": "MHIHOBB",
        "licenceNo": 555555,
        "nbPoints": 1500,
        "phone": "33489653754",
        "totalActualPaid": 0,
    },
)

correct_player_after = (
    {
        "licenceNo": 555555,
        "firstName": "Fjhgzg",
        "lastName": "MHIHOBB",
        "email": "dfqkjqpoe@aieop.com",
        "phone": "33489653754",
        "gender": "F",
        "nbPoints": 1500,
        "club": "USKB",
    },
    after_cutoff,
    {
        "bibNo": None,
        "club": "USKB",
        "email": "dfqkjqpoe@aieop.com",
        "firstName": "Fjhgzg",
        "gender": "F",
        "lastName": "MHIHOBB",
        "licenceNo": 555555,
        "nbPoints": 1500,
        "phone": "33489653754",
        "totalActualPaid": 0,
    },
)

correct_add_player = [
    correct_player_before,
    correct_player_after,
]

incorrect_player_missing_badly_formatted_data = (
    {
        "licenceNo": 55555,
        "lastName": "QSDJKFLQZ",
        "phone": "33688261003",
        "gender": "F",
        "nbPoints": 1500,
        "club": "USKB",
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.PLAYER_FORMAT_MESSAGE,
        payload={
            "email": ["Missing data for required field."],
            "firstName": ["Missing data for required field."],
        },
    ),
)

incorrect_player_duplicate = (
    {
        "licenceNo": 4526124,
        "firstName": "Wihelbl",
        "lastName": "EZWLKRWE",
        "email": "nvzhltrsqr@mochsf.com",
        "phone": "+336919756238",
        "gender": "F",
        "nbPoints": 1149,
        "club": "USM OLIVET TENNIS DE TABLE",
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.DUPLICATE_PLAYER_MESSAGE,
        payload={
            "licenceNo": 4526124,
        },
    ),
)

incorrect_add_player = [
    incorrect_player_missing_badly_formatted_data,
    incorrect_player_duplicate,
]


class TestAPIAdminAddPlayer(BaseTest):
    @pytest.mark.parametrize("payload,now,response", correct_add_player)
    def test_add_player_correct(
        self,
        client,
        reset_db,
        populate,
        payload,
        now: str,
        response,
    ):
        with freeze_time(now):
            r = client.post("/api/admin/players", json=payload)
            assert r.status_code == HTTPStatus.CREATED, r.json
            assert r.json == response, r.json

    @pytest.mark.parametrize("payload,error", incorrect_add_player)
    def test_add_player_incorrect(self, client, reset_db, populate, payload, error):
        r = client.post("/api/admin/players", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error.to_dict(), r.json
