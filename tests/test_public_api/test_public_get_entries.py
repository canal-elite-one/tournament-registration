from http import HTTPStatus
from freezegun import freeze_time

import pytest

import shared.api.api_errors as ae

from tests.conftest import BaseTest, SampleDates


overall_incorrect_licence = "5555555"

origin = "api_public_get_entries"

correct_get_entries_before = (
    "7213526",
    SampleDates.BEFORE_CUTOFF,
    [
        {
            "alternateName": None,
            "categoryId": "2",
            "entryFee": 7,
            "licenceNo": "7213526",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "registrationTime": "2023-03-24T07:14:41",
            "startTime": "2024-01-07T10:15:00",
        },
        {
            "alternateName": None,
            "categoryId": "6",
            "entryFee": 7,
            "licenceNo": "7213526",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "registrationTime": "2023-05-15T21:10:54",
            "startTime": "2024-01-07T15:00:00",
        },
        {
            "alternateName": "< 1500",
            "categoryId": "B",
            "entryFee": 7,
            "licenceNo": "7213526",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "registrationTime": "2023-05-03T04:45:23",
            "startTime": "2024-01-06T10:15:00",
        },
        {
            "alternateName": "Pas open féminin",
            "categoryId": "F",
            "entryFee": 7,
            "licenceNo": "7213526",
            "markedAsPaid": True,
            "markedAsPresent": True,
            "registrationTime": "2023-09-21T07:22:44",
            "startTime": "2024-01-06T15:00:00",
        },
    ],
)

correct_get_entries_after = (
    "7213526",
    SampleDates.AFTER_CUTOFF,
    [
        {
            "alternateName": None,
            "categoryId": "2",
            "entryFee": 7,
            "licenceNo": "7213526",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "registrationTime": "2023-03-24T07:14:41",
            "startTime": "2024-01-07T10:15:00",
        },
        {
            "alternateName": None,
            "categoryId": "6",
            "entryFee": 7,
            "licenceNo": "7213526",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "registrationTime": "2023-05-15T21:10:54",
            "startTime": "2024-01-07T15:00:00",
        },
        {
            "alternateName": "< 1500",
            "categoryId": "B",
            "entryFee": 7,
            "licenceNo": "7213526",
            "markedAsPaid": False,
            "markedAsPresent": None,
            "registrationTime": "2023-05-03T04:45:23",
            "startTime": "2024-01-06T10:15:00",
        },
        {
            "alternateName": "Pas open féminin",
            "categoryId": "F",
            "entryFee": 7,
            "licenceNo": "7213526",
            "markedAsPaid": True,
            "markedAsPresent": True,
            "registrationTime": "2023-09-21T07:22:44",
            "startTime": "2024-01-06T15:00:00",
        },
    ],
)

correct_get_entries = [
    correct_get_entries_before,
    correct_get_entries_after,
]

incorrect_non_existing_player = (
    "5555555",
    SampleDates.BEFORE_CUTOFF,
    ae.PlayerNotFoundError(
        origin=origin,
        licence_no="5555555",
    ),
)


incorrect_get_entries = [
    incorrect_non_existing_player,
]


class TestAPIGetEntries(BaseTest):
    @pytest.mark.parametrize("licence_no,now,response", correct_get_entries)
    def test_correct_get_entries(
        self,
        public_client,
        reset_db,
        populate,
        licence_no,
        now: str,
        response,
    ):
        with freeze_time(now):
            r = public_client.get(f"/api/public/entries/{licence_no}")
            assert r.status_code == HTTPStatus.OK
            assert r.json == response

    @pytest.mark.parametrize("licence_no,now,error", incorrect_get_entries)
    def test_incorrect_get_entries(
        self,
        public_client,
        reset_db,
        populate,
        licence_no,
        now,
        error,
    ):
        error = ae.PlayerNotFoundError(
            origin=origin,
            licence_no=licence_no,
        )
        with freeze_time(now):
            r = public_client.get(f"/api/public/entries/{licence_no}")
            assert r.status_code == error.status_code
            assert r.json == error.to_dict()
