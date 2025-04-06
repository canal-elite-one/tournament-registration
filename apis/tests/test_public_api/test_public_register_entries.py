from http import HTTPStatus

import pytest
from freezegun import freeze_time

import apis.shared.api_errors as ae

from apis.public import BaseTest, SampleDates

overall_correct_licence = "722370"
overall_incorrect_licence = "555555"

origin = "api_public_register_entries"

correct_registration = (
    "7897897",
    SampleDates.BEFORE_CUTOFF,
    {"categoryIds": ["A"]},
    {
        "A": {
            "alternateName": "< 900",
            "entryFee": 7,
            "licenceNo": "7897897",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "rank": 0,
            "registrationTime": "2023-01-01T00:00:00",
            "startTime": "2024-01-06T09:00:00",
        },
    },
)

correct_registration_woman_one_day = (
    "1234567",
    SampleDates.BEFORE_CUTOFF,
    {"categoryIds": ["B", "C"]},
    {
        "B": {
            "alternateName": "< 1500",
            "entryFee": 7,
            "licenceNo": "1234567",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "rank": 0,
            "registrationTime": "2023-01-01T00:00:00",
            "startTime": "2024-01-06T10:15:00",
        },
        "C": {
            "alternateName": None,
            "entryFee": 10,
            "licenceNo": "1234567",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "rank": 0,
            "registrationTime": "2023-01-01T00:00:00",
            "startTime": "2024-01-06T11:30:00",
        },
    },
)

correct_registration_woman_two_days = (
    "1234567",
    SampleDates.BEFORE_CUTOFF,
    {"categoryIds": ["B", "C", "5", "3"]},
    {
        "3": {
            "alternateName": None,
            "entryFee": 7,
            "licenceNo": "1234567",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "rank": 0,
            "registrationTime": "2023-01-01T00:00:00",
            "startTime": "2024-01-07T11:30:00",
        },
        "5": {
            "alternateName": None,
            "entryFee": 7,
            "licenceNo": "1234567",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "rank": 0,
            "registrationTime": "2023-01-01T00:00:00",
            "startTime": "2024-01-07T14:00:00",
        },
        "B": {
            "alternateName": "< 1500",
            "entryFee": 7,
            "licenceNo": "1234567",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "rank": 0,
            "registrationTime": "2023-01-01T00:00:00",
            "startTime": "2024-01-06T10:15:00",
        },
        "C": {
            "alternateName": None,
            "entryFee": 10,
            "licenceNo": "1234567",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "rank": 0,
            "registrationTime": "2023-01-01T00:00:00",
            "startTime": "2024-01-06T11:30:00",
        },
    },
)

correct_registration_woman_three_categories_one_day = (
    "1234567",
    SampleDates.BEFORE_CUTOFF,
    {"categoryIds": ["B", "C", "G"]},
    {
        "B": {
            "alternateName": "< 1500",
            "entryFee": 7,
            "licenceNo": "1234567",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "rank": 0,
            "registrationTime": "2023-01-01T00:00:00",
            "startTime": "2024-01-06T10:15:00",
        },
        "C": {
            "alternateName": None,
            "entryFee": 10,
            "licenceNo": "1234567",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "rank": 0,
            "registrationTime": "2023-01-01T00:00:00",
            "startTime": "2024-01-06T11:30:00",
        },
        "G": {
            "alternateName": None,
            "entryFee": 7,
            "licenceNo": "1234567",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "rank": 0,
            "registrationTime": "2023-01-01T00:00:00",
            "startTime": "2024-01-06T16:00:00",
        },
    },
)

correct_register_entries = [
    correct_registration,
    correct_registration_woman_one_day,
    correct_registration_woman_two_days,
    correct_registration_woman_three_categories_one_day,
]

incorrect_registration_color_violation = (
    "7897897",
    SampleDates.BEFORE_CUTOFF,
    {"categoryIds": ["A", "B"]},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.COLOR_VIOLATION_MESSAGE,
    ),
)

incorrect_registration_gender_points_violation = (
    "7897897",
    SampleDates.BEFORE_CUTOFF,
    {
        "categoryIds": ["C"],
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.GENDER_POINTS_VIOLATION_MESSAGE,
        payload={"categoryIds": ["C"]},
    ),
)

incorrect_registration_nonexisting_player = (
    overall_incorrect_licence,
    SampleDates.BEFORE_CUTOFF,
    {"categoryIds": ["A"]},
    ae.PlayerNotFoundError(
        origin=origin,
        licence_no=overall_incorrect_licence,
    ),
)

incorrect_registrations_missing_categoryids_json_fields = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.REGISTRATION_FORMAT_MESSAGE,
        payload={"categoryIds": ["Missing data for required field."]},
    ),
)

incorrect_registration_empty_categories = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {"categoryIds": []},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.REGISTRATION_MISSING_IDS_MESSAGE,
    ),
)

incorrect_registration_nonexisting_categories = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {
        "categoryIds": ["A", "a"],
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.INVALID_CATEGORY_ID_MESSAGES["registration"],
        payload={"categoryIds": ["a"]},
    ),
)

incorrect_registration_after = (
    "4526124",
    SampleDates.AFTER_CUTOFF,
    {"categoryIds": ["1"]},
    ae.RegistrationCutoffError(
        origin=origin,
        error_message=ae.RegistrationMessages.ENDED,
    ),
)

incorrect_registration_before_registration_start = (
    "4526124",
    SampleDates.BEFORE_START,
    {"categoryIds": ["1"]},
    ae.RegistrationCutoffError(
        origin=origin,
        error_message=ae.RegistrationMessages.NOT_STARTED,
    ),
)

incorrect_registration_mandatory_women_only = (
    "1234567",
    SampleDates.BEFORE_CUTOFF,
    {"categoryIds": ["A"]},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.MANDATORY_WOMEN_ONLY_REGISTRATION_MESSAGE,
        payload={"categoryIdsShouldRegister": ["C"]},
    ),
)

incorrect_registration_max_entries_per_day_man = (
    "7897897",
    SampleDates.BEFORE_CUTOFF,
    {"categoryIds": ["B", "D", "F"]},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.MAX_ENTRIES_PER_DAY_MESSAGE,
    ),
)

incorrect_register_entries = [
    incorrect_registration_color_violation,
    incorrect_registration_gender_points_violation,
    incorrect_registration_nonexisting_player,
    incorrect_registrations_missing_categoryids_json_fields,
    incorrect_registration_empty_categories,
    incorrect_registration_nonexisting_categories,
    incorrect_registration_after,
    incorrect_registration_before_registration_start,
    incorrect_registration_mandatory_women_only,
    incorrect_registration_max_entries_per_day_man,
]


class TestRegisterEntries(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,now,payload,response",
        correct_register_entries,
    )
    def test_correct_register_entries(
        self,
        public_client,
        reset_db,
        populate,
        licence_no,
        now: str,
        payload,
        response,
    ):
        with freeze_time(now):
            r = public_client.post(f"/api/public/entries/{licence_no}", json=payload)
            assert r.status_code == HTTPStatus.CREATED, r.json
            assert "registeredEntries" in r.json, r.json
            assert r.json["registeredEntries"] == response, r.json

    @pytest.mark.parametrize("licence_no,now,payload,error", incorrect_register_entries)
    def test_incorrect_register_entries(
        self,
        public_client,
        reset_db,
        populate,
        licence_no,
        now: str,
        payload,
        error,
    ):
        with freeze_time(now):
            r = public_client.post(f"/api/public/entries/{licence_no}", json=payload)
            assert r.status_code == error.status_code, r.json
            assert r.json == error.to_dict(), r.json
