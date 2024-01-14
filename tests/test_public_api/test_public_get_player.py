from http import HTTPStatus

import pytest
from freezegun import freeze_time

import shared.api.api_errors as ae

from tests.conftest import BaseTest, before_cutoff, after_cutoff


overall_incorrect_licence = 5555555

origin = "api_public_get_player"


correct_get_player_existing = (
    7513006,
    before_cutoff,
    {
        "bibNo": None,
        "club": "KREMLIN BICETRE US",
        "email": None,
        "firstName": "Celine",
        "gender": "F",
        "lastName": "LAY",
        "licenceNo": 7513006,
        "nbPoints": 1232,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 0,
            "totalRegistered": 0,
        },
        "phone": None,
        "registeredEntries": {},
    },
)

correct_get_player = [
    correct_get_player_existing,
]

incorrect_get_player_nonexisting = (
    overall_incorrect_licence,
    False,
    before_cutoff,
    ae.PlayerNotFoundError(
        origin=origin,
        licence_no=overall_incorrect_licence,
    ),
)

incorrect_get_player_db_only = (
    7513006,
    True,
    before_cutoff,
    ae.PlayerNotFoundError(
        origin=origin,
        licence_no=7513006,
    ),
)

incorrect_already_registered = (
    4526124,
    False,
    before_cutoff,
    ae.PlayerAlreadyRegisteredError(
        origin=origin,
        error_message=ae.PLAYER_ALREADY_REGISTERED_MESSAGE,
        payload={"licenceNo": 4526124},
    ),
)


incorrect_after = (
    7513006,
    False,
    after_cutoff,
    ae.RegistrationCutoffError(
        origin=origin,
        error_message=ae.REGISTRATION_MESSAGES["ended"],
    ),
)

incorrect_get_player = [
    incorrect_get_player_nonexisting,
    incorrect_get_player_db_only,
    incorrect_after,
]


class TestGetPlayer(BaseTest):
    @pytest.mark.parametrize("licence_no,now,response", correct_get_player)
    def test_correct_get_player(
        self,
        public_client,
        reset_db,
        populate,
        licence_no,
        now,
        response,
    ):
        with freeze_time(now):
            r = public_client.get(f"/api/public/players/{licence_no}")
            assert r.status_code == HTTPStatus.OK, r.json
            assert r.json == response, r.json

    @pytest.mark.parametrize("licence_no,db_only,now,error", incorrect_get_player)
    def test_incorrect_get_player(
        self,
        public_client,
        reset_db,
        populate,
        licence_no,
        db_only,
        now: str,
        error,
    ):
        url = f"/api/public/players/{licence_no}"
        if db_only:
            url += "?db_only=true"
        with freeze_time(now):
            r = public_client.get(url)
            assert r.status_code == error.status_code, r.json
            assert r.json == error.to_dict(), r.json
