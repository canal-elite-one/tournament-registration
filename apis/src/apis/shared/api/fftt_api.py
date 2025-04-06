import os

import requests
from http import HTTPStatus

import hashlib
import hmac

from datetime import datetime

from xml.etree import ElementTree

from pydantic import ValidationError
from dotenv import load_dotenv

from apis.shared.api.api_errors import (
    FFTTAPIError,
    FFTT_DATA_PARSE_MESSAGE,
    FFTT_BAD_RESPONSE_MESSAGE,
)
from apis.shared.models import FfttPlayer

load_dotenv()


def get_current_formatted_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]


def get_encrypted_timestamp(pwd: str, timestamp: str) -> str:
    # hash password to md5
    encoded_password = hashlib.md5(pwd.encode()).hexdigest()
    # encrypt timestamp with password to sha256
    return hmac.new(
        encoded_password.encode(),
        timestamp.encode(),
        hashlib.sha1,
    ).hexdigest()


def get_player_fftt(licence_no) -> FfttPlayer:
    url = os.environ.get("FFTT_API_URL") + "/xml_licence.php"

    tm = get_current_formatted_timestamp()

    serial_no = os.environ["FFTT_SERIAL_NO"]
    app_id = os.environ["FFTT_APP_ID"]
    password = os.environ["FFTT_PASSWORD"]

    tmc = get_encrypted_timestamp(password, tm)
    params = {
        "serie": serial_no,
        "id": app_id,
        "licence": licence_no,
        "tm": tm,
        "tmc": tmc,
    }
    response = requests.get(url, params=params)

    if response.status_code != HTTPStatus.OK:
        raise FFTTAPIError(
            message=FFTT_BAD_RESPONSE_MESSAGE,
            payload={"status_code": response.status_code},
        )

    xml = response.content.decode("ISO-8859-1")
    root = ElementTree.fromstring(xml).find("licence")

    if root is None:
        return None

    try:
        return FfttPlayer(
            licence_no=root.find("licence").text,
            first_name=root.find("prenom").text,
            last_name=root.find("nom").text,
            club=root.find("nomclub").text,
            gender=root.find("sexe").text,
            nb_points=int(root.find("point").text),
        )
    except AttributeError | ValidationError as e:
        message = e.messages if isinstance(e, ValidationError) else str(e)
        raise FFTTAPIError(
            message=FFTT_DATA_PARSE_MESSAGE,
            payload={
                "xml": xml,
                "original_error_message": message,
            },
        )
