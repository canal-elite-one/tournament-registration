from conftest import BaseTest
from http import HTTPStatus
import pytest


correct_player = (
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

correct_add_player = [correct_player]

incorrect_player_missing_badly_formatted_data = (
    {
        "licenceNo": 55555,
        "lastName": "QSDJKFLQZ",
        "phone": "33688261003",
        "gender": "F",
        "nbPoints": 1500,
        "club": "USKB",
    },
    {
        "error": {
            "email": ["Missing data for required field."],
            "firstName": ["Missing data for required field."],
        },
    },
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
    {
        "error": "A player with this licence already exists in the database. "
        "Player was not added.",
    },
)

incorrect_add_player = [
    incorrect_player_missing_badly_formatted_data,
    incorrect_player_duplicate,
]


class TestAPIAddPlayer(BaseTest):
    @pytest.mark.parametrize("payload,response", correct_add_player)
    def test_correct_add_player(self, client, reset_db, populate, payload, response):
        r = client.post("/api/public/players", json=payload)
        assert r.status_code == HTTPStatus.CREATED, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize("payload, error", incorrect_add_player)
    def test_incorrect_add_player(self, client, reset_db, populate, payload, error):
        r = client.post("/api/public/players", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json
