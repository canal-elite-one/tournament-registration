import traceback

from flask import jsonify
from http import HTTPStatus


def handle_api_error(error):
    return jsonify(error.to_dict()), error.status_code


class FFTTAPIError(Exception):
    def __init__(self, payload=None):
        super().__init__()
        self.payload = payload


class APIError(Exception):
    """Base class for API errors"""

    status_code: int
    error_type: str

    def __init__(self, origin=None, error_message=None, payload=None):
        super().__init__()
        self.error_message = error_message
        self.origin = origin
        self.payload = payload

    def to_dict(self) -> dict:
        return {
            "errorType": self.error_type,
            "origin": self.origin,
            "errorMessage": self.error_message,
            "payload": self.payload,
        }


"""
----------------  400  ----------------
"""


class APIBadRequestError(APIError):
    """Base class for 400 errors"""

    status_code = HTTPStatus.BAD_REQUEST


class RegistrationCutoffError(APIBadRequestError):
    error_type = "REGISTRATION_CUTOFF_ERROR"


REGISTRATION_MESSAGES = {
    "not_started": "Registration has not started yet",
    "ended": "Registration has already ended",
    "started": "Registration has already started",
    "not_ended": "Registration has not ended yet",
    "not_ended_mark_present": "Registration has not ended "
    "yet, can only mark players as absent",
}


class InvalidDataError(APIBadRequestError):
    error_type = "INVALID_DATA"


CATEGORY_FORMAT_MESSAGE = "Some category data is missing or badly formatted"
PLAYER_FORMAT_MESSAGE = "Some player data is missing or badly formatted"
REGISTRATION_FORMAT_MESSAGE = "Some registration data is missing or badly formatted"
DELETE_ENTRIES_FORMAT_MESSAGE = (
    "Some data for entry deletion is missing or badly formatted"
)
PAYMENT_FORMAT_MESSAGE = "Some payment data is missing or badly formatted"

GENDER_POINTS_VIOLATION_MESSAGE = (
    "Tried to register some entries violating either gender or points conditions"
)
COLOR_VIOLATION_MESSAGE = (
    "Tried to register some entries violating the color constraint"
)

REGISTRATION_MISSING_IDS_MESSAGE = "No category ids to register to were provided"


INVALID_CATEGORY_ID_MESSAGES = {
    "registration": (
        "Some category ids do not correspond to any category in the database"
    ),
    "deletion": (
        "Some category ids either do not correspond to any category "
        "in the database, or the player is not registered to it"
    ),
    "payment": (
        "Some category ids either do not correspond to any category "
        "in the database, the player is not registered to it, "
        "or is not marked as present for it"
    ),
    "present": (
        "Some category ids either do not correspond to any category "
        "in the database, or the player is not registered to it"
    ),
}

ACTUAL_PAID_TOO_HIGH_MESSAGE = (
    "The 'totalActualPaid' field is higher than what the player must "
    "currently pay for all categories he is marked as present"
)

DUPLICATE_PLAYER_MESSAGE = (
    "A player with this licence number already exists in the database"
)

CATEGORY_FULL_PRESENT_MESSAGE = (
    "Some categories are already full of present players, and the player "
    "thus cannot be marked as present for these."
)

MAX_ENTRIES_PER_DAY_MESSAGE = (
    "Tried to register more than the maximum number of categories for a single day"
)

"""
----------------  403  ----------------
"""


class APIForbiddenError(APIError):
    """Base class for 403 errors"""

    status_code = HTTPStatus.FORBIDDEN


class ConfirmationError(APIForbiddenError):
    error_type = "CONFIRMATION_ERROR"


class PlayerAlreadyRegisteredError(APIForbiddenError):
    error_type = "PLAYER_ALREADY_REGISTERED"


PLAYER_ALREADY_REGISTERED_MESSAGE = (
    "This player is already registered, can only fetch entries"
)

RESET_BIBS_CONFIRMATION = "Je suis sur! J'ai appelé Céline!"
RESET_BIBS_CONFIRMATION_MESSAGE = "Missing or incorrect confirmation message."


"""
----------------  404  ----------------
"""


class APINotFoundError(APIError):
    """Base class for 404 errors"""

    status_code = HTTPStatus.NOT_FOUND


class PlayerNotFoundError(APINotFoundError):
    error_type = "PLAYER_NOT_FOUND"

    def __init__(self, origin=None, licence_no=None):
        payload = {
            "licenceNo": licence_no,
        }
        super().__init__(
            origin=origin,
            error_message="No player with this licence number was found",
            payload=payload,
        )


"""
----------------  409  ----------------
"""


class APIConflictError(APIError):
    """Base class for 409 errors"""

    status_code = HTTPStatus.CONFLICT


class BibConflictError(APIConflictError):
    error_type = "BIB_CONFLICT"


SOME_BIBS_ALREADY_ASSIGNED_MESSAGE = "Some players already have a bib number assigned"
THIS_BIB_ALREADY_ASSIGNED_MESSAGE = "This player already has a bib number assigned"
NO_BIBS_ASSIGNED_MESSAGE = (
    "No bib numbers have been assigned yet, cannot assign them individually"
)


"""
----------------  500  ----------------
"""


class UnexpectedAPIError(APIError):
    """Base class for Python 500 errors"""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, origin=None, error_message=None, exception=None):
        payload = {
            "exceptionType": type(exception).__name__,
            "exceptionMessage": str(exception),
            "traceback": traceback.format_exc(),
        }
        super().__init__(origin=origin, error_message=error_message, payload=payload)


class UnexpectedDBError(UnexpectedAPIError):
    error_type = "UNEXPECTED_DB_ERROR"

    def __init__(self, origin=None, exception=None):
        super().__init__(
            origin=origin,
            error_message="An unexpected error occurred while accessing the database",
            exception=exception,
        )


class UnexpectedFFTTError(APIError):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_type = "UNEXPECTED_FFTT_ERROR"

    def __init__(self, origin=None, payload=None):
        super().__init__(
            origin=origin,
            error_message="An unexpected error occurred while accessing the FFTT API",
            payload=payload,
        )
