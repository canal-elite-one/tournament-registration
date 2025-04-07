import requests
from http import HTTPStatus

import hashlib
import hmac

from datetime import datetime

from xml.etree import ElementTree

from flask import current_app
from marshmallow import ValidationError

from api.shared.api.api_errors import (
    FFTTAPIError,
    FFTT_DATA_PARSE_MESSAGE,
    FFTT_BAD_RESPONSE_MESSAGE,
)
from api.shared.api.marshmallow_schemas import PlayerSchema


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


def get_player_fftt(licence_no):
    url = current_app.config.get("FFTT_API_URL") + "/xml_licence.php"

    tm = get_current_formatted_timestamp()

    serial_no = current_app.config["FFTT_SERIAL_NO"]
    app_id = current_app.config["FFTT_APP_ID"]
    password = current_app.config["FFTT_PASSWORD"]

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

    p_schema = PlayerSchema()

    try:
        return p_schema.load(
            {
                "licenceNo": root.find("licence").text,
                "firstName": root.find("prenom").text,
                "lastName": root.find("nom").text,
                "club": root.find("nomclub").text,
                "gender": root.find("sexe").text,
                "nbPoints": int(root.find("point").text),
            },
        )
    except (ValidationError, AttributeError) as e:
        message = e.messages if isinstance(e, ValidationError) else str(e)
        raise FFTTAPIError(
            message=FFTT_DATA_PARSE_MESSAGE,
            payload={
                "xml": xml,
                "original_error_message": message,
            },
        )
