from http import HTTPStatus

import pytest
import requests_mock
from freezegun import freeze_time

import shared.api.api_errors as ae

from tests.conftest import BaseTest, SampleDates

overall_incorrect_licence = "5555555"

origin = "api_public_get_player"

correct_get_player_existing = (
    "7513006",
    SampleDates.BEFORE_CUTOFF,
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
        "totalActualPaid": 0,
        "phone": None,
    },
)

correct_get_player = [
    correct_get_player_existing,
]

empty_xml = b'<?xml version="1.0" encoding="ISO-8859-1"?>\n<liste/>'

incorrect_get_player_nonexisting = (
    overall_incorrect_licence,
    SampleDates.BEFORE_CUTOFF,
    empty_xml,
    ae.PlayerNotFoundError(
        origin=origin,
        licence_no=overall_incorrect_licence,
    ),
)

incorrect_already_registered = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    empty_xml,
    ae.PlayerAlreadyRegisteredError(
        origin=origin,
        error_message=ae.PLAYER_ALREADY_REGISTERED_MESSAGE,
        payload={"licenceNo": "4526124"},
    ),
)

incorrect_after = (
    "7513006",
    SampleDates.AFTER_CUTOFF,
    empty_xml,
    ae.RegistrationCutoffError(
        origin=origin,
        error_message=ae.RegistrationMessages.ENDED,
    ),
)

incorrect_parse_error_missing = (
    "7513006",
    SampleDates.BEFORE_CUTOFF,
    b'<?xml version="1.0" '
    b'encoding="ISO-8859-1"?>\n<liste><licence><idlicence'
    b">375537</idlicence><licence>7513006</licence><nom>LAY"
    b"</nom><prenom>Celine</prenom><numclub>08940975</numclub"
    b"><nomclub>KREMLIN BICETRE "
    b"US</nomclub><type>T</type><certif>A"
    b"</certif><validation>04/07/2023</validation><echelon"
    b"></echelon><place/><point>1232</point><cat>Seniors</cat"
    b"></licence></liste>",
    ae.UnexpectedFFTTError(
        origin=origin,
        message=ae.FFTT_DATA_PARSE_MESSAGE,
        payload={
            "original_error_message": "'NoneType' object has no attribute " "'text'",
            "xml": '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
            "<liste><licence><idlicence>375537</idlicence><licence>7513006"
            "</licence><nom>LAY</nom><prenom>Celine</prenom><numclub>08940975"
            "</numclub><nomclub>KREMLIN BICETRE US</nomclub>"
            "<type>T</type><certif>A</certif><validation>04/07"
            "/2023</validation><echelon></echelon><place/><point>1232</point>"
            "<cat>Seniors</cat></licence></liste>",
        },
    ),
)

incorrect_get_player = [
    incorrect_get_player_nonexisting,
    incorrect_already_registered,
    incorrect_after,
    incorrect_parse_error_missing,
]


class TestGetPlayer(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,now,fftt_response,response",
        correct_get_player,
    )
    def test_correct_get_player(
        self,
        public_app,
        public_client,
        reset_db,
        populate,
        licence_no,
        now: str,
        fftt_response,
        response,
    ):
        with freeze_time(now), requests_mock.Mocker() as m:
            m.get(
                f"{public_app.config.get('FFTT_API_URL')}/xml_licence.php",
                status_code=HTTPStatus.OK,
                content=fftt_response,
            )
            r = public_client.get(f"/api/public/players/{licence_no}")
            assert r.status_code == HTTPStatus.OK, r.json
            assert r.json == response, r.json

    @pytest.mark.parametrize("licence_no,now,fftt_response,error", incorrect_get_player)
    def test_incorrect_get_player(
        self,
        public_app,
        public_client,
        reset_db,
        populate,
        licence_no,
        now: str,
        fftt_response,
        error,
    ):
        url = f"/api/public/players/{licence_no}"
        with freeze_time(now), requests_mock.Mocker() as m:
            m.get(
                f"{public_app.config.get('FFTT_API_URL')}/xml_licence.php",
                status_code=HTTPStatus.OK,
                content=fftt_response,
            )
            r = public_client.get(url)
            assert r.status_code == error.status_code, r.json
            assert r.json == error.to_dict(), r.json

    def test_get_player_fftt_error(
        self,
        public_app,
        public_client,
        reset_db,
        populate,
    ):
        with freeze_time(SampleDates.BEFORE_CUTOFF), requests_mock.Mocker() as m:
            m.get(
                f"{public_app.config.get('FFTT_API_URL')}/xml_licence.php",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            r = public_client.get("/api/public/players/4562159")
            assert r.status_code == HTTPStatus.INTERNAL_SERVER_ERROR, r.json
            assert (
                r.json
                == ae.UnexpectedFFTTError(
                    origin=origin,
                    message=ae.FFTT_BAD_RESPONSE_MESSAGE,
                    payload={"status_code": HTTPStatus.INTERNAL_SERVER_ERROR},
                ).to_dict()
            ), r.json
