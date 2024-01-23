from http import HTTPStatus

import pytest
import requests_mock
from freezegun import freeze_time

import shared.api.api_errors as ae

from tests.conftest import BaseTest, before_cutoff, after_cutoff

origin = "api_admin_get_player"

correct_db_before = (
    "9943272",
    before_cutoff,
    b"",
    {
        "bibNo": None,
        "club": "NANTES ST MEDARD DOULON",
        "email": "player24@emailhost.com",
        "firstName": "Player24",
        "gender": "M",
        "lastName": "AERGTHVI",
        "licenceNo": "9943272",
        "nbPoints": 1583,
        "phone": "+33806956124",
        "registeredEntries": {
            "E": {
                "alternateName": None,
                "entryFee": 10,
                "licenceNo": "9943272",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 44,
                "registrationTime": "2023-12-23T16:27:46.012875",
                "startTime": "2024-01-06T14:00:00",
            },
        },
    },
)

correct_db_after = (
    "9943272",
    after_cutoff,
    b"",
    {
        "bibNo": None,
        "club": "NANTES ST MEDARD DOULON",
        "email": "player24@emailhost.com",
        "firstName": "Player24",
        "gender": "M",
        "lastName": "AERGTHVI",
        "leftToPay": 0,
        "licenceNo": "9943272",
        "nbPoints": 1583,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 0,
            "totalRegistered": 10,
        },
        "phone": "+33806956124",
        "registeredEntries": {
            "E": {
                "alternateName": None,
                "entryFee": 10,
                "licenceNo": "9943272",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 44,
                "registrationTime": "2023-12-23T16:27:46.012875",
                "startTime": "2024-01-06T14:00:00",
            },
        },
    },
)

correct_fftt_before = (
    "7513006",
    before_cutoff,
    b'<?xml version="1.0" '
    b'encoding="ISO-8859-1"?>\n<liste><licence><idlicence'
    b">375537</idlicence><licence>7513006</licence><nom>LAY"
    b"</nom><prenom>Celine</prenom><numclub>08940975</numclub"
    b"><nomclub>KREMLIN BICETRE "
    b"US</nomclub><sexe>F</sexe><type>T</type><certif>A"
    b"</certif><validation>04/07/2023</validation><echelon"
    b"></echelon><place/><point>1232</point><cat>Seniors</cat"
    b"></licence></liste>",
    {
        "bibNo": None,
        "club": "KREMLIN BICETRE US",
        "email": None,
        "firstName": "Celine",
        "gender": "F",
        "lastName": "LAY",
        "licenceNo": "7513006",
        "nbPoints": 1232,
        "phone": None,
        "totalActualPaid": None,
    },
)

correct_licences = [
    correct_db_before,
    correct_db_after,
    correct_fftt_before,
]

incorrect_licence = (
    "1234567",
    False,
    ae.PlayerNotFoundError(
        origin=origin,
        licence_no="1234567",
    ),
)

incorrect_licence_db_only = (
    "7513006",
    True,
    ae.PlayerNotFoundError(
        origin=origin + "_db_only",
        licence_no="7513006",
    ),
)

incorrect_licences = [incorrect_licence, incorrect_licence_db_only]


class TestAPIAdminGetPlayer(BaseTest):
    @pytest.mark.parametrize("licence_no,now,fftt_response,response", correct_licences)
    def test_get_player_correct(
        self,
        admin_app,
        admin_client,
        reset_db,
        populate,
        licence_no,
        now: str,
        fftt_response,
        response,
    ):
        with freeze_time(now), requests_mock.Mocker() as m:
            m.get(
                f"{admin_app.config.get('FFTT_API_URL')}/xml_licence.php",
                status_code=HTTPStatus.OK,
                content=fftt_response,
            )
            r = admin_client.get(f"/api/admin/players/{licence_no}")
            assert r.status_code == HTTPStatus.OK, r.json
            assert r.json == response, r.json

    @pytest.mark.parametrize("licence_no,db_only,error", incorrect_licences)
    def test_get_player_incorrect(
        self,
        admin_app,
        admin_client,
        reset_db,
        populate,
        licence_no,
        db_only,
        error,
    ):
        with requests_mock.Mocker() as m:
            m.get(
                f"{admin_app.config.get('FFTT_API_URL')}/xml_licence.php",
                status_code=HTTPStatus.OK,
                content=b'<?xml version="1.0" encoding="ISO-8859-1"?>\n<liste/>',
            )
            r = admin_client.get(
                f"/api/admin/players/{licence_no}?"
                f"db_only={'true' if db_only else 'false'}",
            )
            assert r.status_code == error.status_code
            assert r.json == error.to_dict(), r.json

    def test_get_player_fftt_error(
        self,
        admin_app,
        admin_client,
        reset_db,
        populate,
    ):
        with requests_mock.Mocker() as m:
            m.get(
                f"{admin_app.config.get('FFTT_API_URL')}/xml_licence.php",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            r = admin_client.get("/api/admin/players/1234567")
            assert r.status_code == HTTPStatus.INTERNAL_SERVER_ERROR, r.json
            assert (
                r.json
                == ae.UnexpectedFFTTError(
                    origin=origin,
                    message=ae.FFTT_BAD_RESPONSE_MESSAGE,
                    payload={"status_code": HTTPStatus.INTERNAL_SERVER_ERROR},
                ).to_dict()
            ), r.json
