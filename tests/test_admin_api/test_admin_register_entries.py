from http import HTTPStatus

from freezegun import freeze_time
import pytest

import shared.api.api_errors as ae

from tests.conftest import BaseTest, SampleDates

overall_correct_licence = "722370"
no_entries_licence = "7897897"
overall_incorrect_licence = "555555"
origin = "api_admin_register_entries"

correct_registration_before = (
    no_entries_licence,
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    {
        "bibNo": None,
        "club": "LAVAL Francs Archers",
        "email": "noentries@noentries.com",
        "firstName": "NoEntries",
        "gender": "M",
        "lastName": "NOENTRIES",
        "licenceNo": "7897897",
        "nbPoints": 900,
        "phone": "+33600000000",
        "registeredEntries": {
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
    },
)

correct_registration_before_missing_total_actual_paid = (
    no_entries_licence,
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
        ],
    },
    {
        "bibNo": None,
        "club": "LAVAL Francs Archers",
        "email": "noentries@noentries.com",
        "firstName": "NoEntries",
        "gender": "M",
        "lastName": "NOENTRIES",
        "licenceNo": "7897897",
        "nbPoints": 900,
        "phone": "+33600000000",
        "registeredEntries": {
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
    },
)

correct_registration_after = (
    no_entries_licence,
    SampleDates.AFTER_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    {
        "bibNo": None,
        "club": "LAVAL Francs Archers",
        "email": "noentries@noentries.com",
        "firstName": "NoEntries",
        "gender": "M",
        "lastName": "NOENTRIES",
        "leftToPay": 0,
        "licenceNo": "7897897",
        "nbPoints": 900,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 0,
            "totalRegistered": 8,
        },
        "phone": "+33600000000",
        "registeredEntries": {
            "A": {
                "alternateName": "< 900",
                "entryFee": 8,
                "licenceNo": "7897897",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 123,
                "registrationTime": "2025-01-01T00:00:00",
                "startTime": "2024-01-06T09:00:00",
            },
        },
    },
)

correct_registration_before_with_deletion = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "1", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    {
        "bibNo": None,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "licenceNo": "4526124",
        "nbPoints": 1149,
        "phone": "+336919756238",
        "registeredEntries": {
            "1": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": "4526124",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 0,
                "registrationTime": "2023-01-01T00:00:00",
                "startTime": "2024-01-07T09:00:00",
            },
        },
    },
)

correct_registration_after_with_deletion = (
    "4526124",
    SampleDates.AFTER_CUTOFF,
    {
        "entries": [
            {"categoryId": "1", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    {
        "bibNo": None,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "leftToPay": 0,
        "licenceNo": "4526124",
        "nbPoints": 1149,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 0,
            "totalRegistered": 8,
        },
        "phone": "+336919756238",
        "registeredEntries": {
            "1": {
                "alternateName": None,
                "entryFee": 8,
                "licenceNo": "4526124",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 136,
                "registrationTime": "2025-01-01T00:00:00",
                "startTime": "2024-01-07T09:00:00",
            },
        },
    },
)

correct_registration_before_with_update = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "1", "markedAsPaid": False, "markedAsPresent": None},
            {"categoryId": "B", "markedAsPaid": False, "markedAsPresent": False},
            {"categoryId": "F", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    {
        "bibNo": None,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "licenceNo": "4526124",
        "nbPoints": 1149,
        "phone": "+336919756238",
        "registeredEntries": {
            "1": {
                "alternateName": None,
                "entryFee": 7,
                "licenceNo": "4526124",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 0,
                "registrationTime": "2023-01-01T00:00:00",
                "startTime": "2024-01-07T09:00:00",
            },
            "B": {
                "alternateName": "< 1500",
                "entryFee": 7,
                "licenceNo": "4526124",
                "markedAsPaid": False,
                "markedAsPresent": False,
                "rank": 43,
                "registrationTime": "2023-11-17T18:01:20",
                "startTime": "2024-01-06T10:15:00",
            },
            "F": {
                "alternateName": "Pas open féminin",
                "entryFee": 7,
                "licenceNo": "4526124",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 30,
                "registrationTime": "2023-11-25T21:56:50",
                "startTime": "2024-01-06T15:00:00",
            },
        },
    },
)

correct_registration_after_with_update = (
    "4526124",
    SampleDates.AFTER_CUTOFF,
    {
        "entries": [
            {"categoryId": "B", "markedAsPaid": False, "markedAsPresent": None},
            {"categoryId": "F", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    {
        "bibNo": None,
        "club": "USM OLIVET TENNIS DE TABLE",
        "email": "nvzhltrsqr@mochsf.com",
        "firstName": "Wihelbl",
        "gender": "F",
        "lastName": "EZWLKRWE",
        "leftToPay": 0,
        "licenceNo": "4526124",
        "nbPoints": 1149,
        "paymentStatus": {
            "totalActualPaid": 0,
            "totalPaid": 0,
            "totalPresent": 0,
            "totalRegistered": 14,
        },
        "phone": "+336919756238",
        "registeredEntries": {
            "B": {
                "alternateName": "< 1500",
                "entryFee": 7,
                "licenceNo": "4526124",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 43,
                "registrationTime": "2023-11-17T18:01:20",
                "startTime": "2024-01-06T10:15:00",
            },
            "F": {
                "alternateName": "Pas open féminin",
                "entryFee": 7,
                "licenceNo": "4526124",
                "markedAsPaid": False,
                "markedAsPresent": None,
                "rank": 30,
                "registrationTime": "2023-11-25T21:56:50",
                "startTime": "2024-01-06T15:00:00",
            },
        },
    },
)

correct_register_entries = [
    correct_registration_before,
    correct_registration_after,
    correct_registration_before_missing_total_actual_paid,
    correct_registration_before_with_deletion,
    correct_registration_after_with_deletion,
    correct_registration_before_with_update,
    correct_registration_after_with_update,
]

color_violation_before = (
    "7886249",
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "1", "markedAsPaid": False, "markedAsPresent": None},
            {"categoryId": "2", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.COLOR_VIOLATION_MESSAGE,
    ),
)

color_violation_after = (
    "7886249",
    SampleDates.AFTER_CUTOFF,
    {
        "entries": [
            {"categoryId": "1", "markedAsPaid": False, "markedAsPresent": None},
            {"categoryId": "2", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.COLOR_VIOLATION_MESSAGE,
    ),
)

gender_points_violation_before = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.GENDER_POINTS_VIOLATION_MESSAGE,
        payload={"categoryIds": ["A"]},
    ),
)

gender_points_violation_after = (
    "4526124",
    SampleDates.AFTER_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.GENDER_POINTS_VIOLATION_MESSAGE,
        payload={"categoryIds": ["A"]},
    ),
)

nonexisting_player_before = (
    overall_incorrect_licence,
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    ae.PlayerNotFoundError(origin=origin, licence_no=overall_incorrect_licence),
)

nonexisting_player_after = (
    overall_incorrect_licence,
    SampleDates.AFTER_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    ae.PlayerNotFoundError(origin=origin, licence_no=overall_incorrect_licence),
)

missing_entries_json_field_before = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {
        "totalActualPaid": 0,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.REGISTRATION_FORMAT_MESSAGE,
        payload={"json": ["json payload should have 'entries' field."]},
    ),
)

missing_entries_json_field_after = (
    "4526124",
    SampleDates.AFTER_CUTOFF,
    {
        "totalActualPaid": 0,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.REGISTRATION_FORMAT_MESSAGE,
        payload={"json": ["json payload should have 'entries' field."]},
    ),
)

entry_format_before = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False},
        ],
        "totalActualPaid": 0,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.REGISTRATION_FORMAT_MESSAGE,
        payload={"0": {"markedAsPresent": ["Missing data for required field."]}},
    ),
)

entry_format_after = (
    "4526124",
    SampleDates.AFTER_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False},
        ],
        "totalActualPaid": 0,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.REGISTRATION_FORMAT_MESSAGE,
        payload={"0": {"markedAsPresent": ["Missing data for required field."]}},
    ),
)

nonzero_totalactualpaid_json_field_before = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 1,
    },
    ae.RegistrationCutoffError(
        origin=origin,
        error_message=ae.RegistrationMessages.NOT_ENDED_ACTUAL_MAKE_PAYMENT,
        payload={"totalActualPaid": 1},
    ),
)

missing_totalactualpaid_json_field_after = (
    "4526124",
    SampleDates.AFTER_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
        ],
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.PAYMENT_FORMAT_MESSAGE,
        payload={"totalActualPaid": "Field is missing or null"},
    ),
)

nonexisting_categories_before = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
            {"categoryId": "a", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.INVALID_CATEGORY_ID_MESSAGES["registration"],
        payload={"categoryIds": ["a"]},
    ),
)

nonexisting_categories_after = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "A", "markedAsPaid": False, "markedAsPresent": None},
            {"categoryId": "a", "markedAsPaid": False, "markedAsPresent": None},
        ],
        "totalActualPaid": 0,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.INVALID_CATEGORY_ID_MESSAGES["registration"],
        payload={"categoryIds": ["a"]},
    ),
)

mark_present_before = (
    "4526124",
    SampleDates.BEFORE_CUTOFF,
    {
        "entries": [
            {"categoryId": "1", "markedAsPaid": False, "markedAsPresent": True},
        ],
        "totalActualPaid": 0,
    },
    ae.RegistrationCutoffError(
        origin=origin,
        error_message=ae.RegistrationMessages.NOT_ENDED_MARK_PRESENT_MAKE_PAYMENT,
        payload={"categoryIdsPaid": [], "categoryIdsPresent": ["1"]},
    ),
)

payment_without_present_after = (
    "4526124",
    SampleDates.AFTER_CUTOFF,
    {
        "entries": [
            {"categoryId": "1", "markedAsPaid": True, "markedAsPresent": None},
        ],
        "totalActualPaid": 7,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.PAYMENT_PRESENT_VIOLATION_MESSAGE,
        payload={"categoryIds": ["1"]},
    ),
)

total_actual_paid_too_high_after = (
    "4526124",
    SampleDates.AFTER_CUTOFF,
    {
        "entries": [
            {"categoryId": "1", "markedAsPaid": True, "markedAsPresent": True},
        ],
        "totalActualPaid": 20,
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.ACTUAL_PAID_TOO_HIGH_MESSAGE,
        payload={"totalActualPaid": 20, "totalPresent": 8},
    ),
)

incorrect_register_entries = [
    color_violation_before,
    color_violation_after,
    gender_points_violation_before,
    gender_points_violation_after,
    nonexisting_player_before,
    nonexisting_player_after,
    missing_entries_json_field_before,
    missing_entries_json_field_after,
    entry_format_before,
    entry_format_after,
    nonzero_totalactualpaid_json_field_before,
    missing_totalactualpaid_json_field_after,
    nonexisting_categories_before,
    nonexisting_categories_after,
    mark_present_before,
    payment_without_present_after,
    total_actual_paid_too_high_after,
]


class TestRegisterEntries(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,now,payload,response",
        correct_register_entries,
    )
    def test_correct_register_entries(
        self,
        admin_client,
        reset_db,
        populate,
        licence_no,
        now: str,
        payload,
        response,
    ):
        with freeze_time(now):
            r = admin_client.post(f"/api/admin/entries/{licence_no}", json=payload)
            assert r.status_code == HTTPStatus.CREATED, r.json
            assert r.json == response, r.json

    @pytest.mark.parametrize("licence_no,now,payload,error", incorrect_register_entries)
    def test_incorrect_register_entries(
        self,
        admin_client,
        reset_db,
        populate,
        licence_no,
        now: str,
        payload,
        error,
    ):
        with freeze_time(now):
            r = admin_client.post(f"/api/admin/entries/{licence_no}", json=payload)
            assert r.status_code == error.status_code, r.json
            assert r.json == error.to_dict(), r.json
