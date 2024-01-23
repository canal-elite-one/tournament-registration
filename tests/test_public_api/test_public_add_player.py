from http import HTTPStatus

import pytest
import requests_mock
from freezegun import freeze_time

import shared.api.api_errors as ae

from tests.conftest import BaseTest, before_cutoff, after_cutoff

origin = "api_public_add_player"

correct_player = (
    "555555",
    {
        "email": "dfqkjqpoe@aieop.com",
        "phone": "33489653754",
    },
    before_cutoff,
    b'<?xml version="1.0" '
    b'encoding="ISO-8859-1"?>\n<liste><licence><idlicence'
    b">375537</idlicence><licence>555555</licence><nom>MHIHOBB"
    b"</nom><prenom>Fjhgzg</prenom><numclub>08940975</numclub"
    b"><nomclub>USKB</nomclub><sexe>F</sexe><type>T</type><certif>A"
    b"</certif><validation>04/07/2023</validation><echelon"
    b"></echelon><place/><point>1500</point><cat>Seniors</cat"
    b"></licence></liste>",
    {
        "bibNo": None,
        "club": "USKB",
        "email": "dfqkjqpoe@aieop.com",
        "firstName": "Fjhgzg",
        "gender": "F",
        "lastName": "MHIHOBB",
        "licenceNo": "555555",
        "nbPoints": 1500,
        "phone": "33489653754",
        "totalActualPaid": 0,
    },
)

correct_add_player = [correct_player]

incorrect_player_missing_badly_formatted_data = (
    "555555",
    {
        "phone": "33688261003",
    },
    before_cutoff,
    b"",
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.PLAYER_CONTACT_FORMAT_MESSAGE,
        payload={
            "email": ["Missing data for required field."],
        },
    ),
)

incorrect_player_duplicate = (
    "4526124",
    {
        "email": "nvzhltrsqr@mocsf.com",
        "phone": "+336919756238",
    },
    before_cutoff,
    b'<?xml version="1.0" '
    b'encoding="ISO-8859-1"?>\n<liste><licence><idlicence'
    b">375537</idlicence><licence>4526124</licence><nom>LAY"
    b"</nom><prenom>Celine</prenom><numclub>08940975</numclub"
    b"><nomclub>KREMLIN BICETRE "
    b"US</nomclub><sexe>F</sexe><type>T</type><certif>A"
    b"</certif><validation>04/07/2023</validation><echelon"
    b"></echelon><place/><point>1232</point><cat>Seniors</cat"
    b"></licence></liste>",
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.DUPLICATE_PLAYER_MESSAGE,
        payload={"licenceNo": "4526124"},
    ),
)

incorrect_after = (
    "555555",
    {
        "licenceNo": "555555",
        "firstName": "Fjhgzg",
        "lastName": "MHIHOBB",
        "email": "fdsqjklq@dfjhk.com",
        "phone": "+33489653754",
        "gender": "F",
        "nbPoints": 1500,
        "club": "USKB",
    },
    after_cutoff,
    b"",
    ae.RegistrationCutoffError(
        origin=origin,
        error_message=ae.REGISTRATION_MESSAGES["ended"],
    ),
)

incorrect_add_player = [
    incorrect_player_missing_badly_formatted_data,
    incorrect_player_duplicate,
    incorrect_after,
]


class TestAPIAddPlayer(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,payload,now,fftt_response,response",
        correct_add_player,
    )
    def test_correct_add_player(
        self,
        public_app,
        public_client,
        reset_db,
        populate,
        licence_no,
        payload,
        now,
        fftt_response,
        response,
    ):
        with freeze_time(now), requests_mock.Mocker() as m:
            m.get(
                f"{public_app.config.get('FFTT_API_URL')}/xml_licence.php",
                status_code=HTTPStatus.OK,
                content=fftt_response,
            )
            r = public_client.post(f"/api/public/players/{licence_no}", json=payload)
            assert r.status_code == HTTPStatus.CREATED, r.json
            assert r.json == response, r.json

    @pytest.mark.parametrize(
        "licence_no,payload,now,fftt_response,error",
        incorrect_add_player,
    )
    def test_incorrect_add_player(
        self,
        public_app,
        public_client,
        reset_db,
        populate,
        licence_no,
        payload,
        now: str,
        fftt_response,
        error,
    ):
        with freeze_time(now), requests_mock.Mocker() as m:
            m.get(
                f"{public_app.config.get('FFTT_API_URL')}/xml_licence.php",
                status_code=HTTPStatus.OK,
                content=fftt_response,
            )
            r = public_client.post(f"/api/public/players/{licence_no}", json=payload)
            assert r.status_code == error.status_code, r.json
            assert r.json == error.to_dict(), r.json
