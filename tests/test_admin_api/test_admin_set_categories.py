from datetime import datetime
from http import HTTPStatus

from tests.conftest import BaseTest
import flaskr.api.api_errors as ae

import pytest


origin = "api_admin_set_categories"

correct_categories = (
    {
        "categories": [
            {
                "categoryId": "a",
                "color": "#FF0000",
                "maxPoints": 1500,
                "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                    "%Y-%m-%dT%H:%M:%S",
                ),
                "baseRegistrationFee": 10,
                "lateRegistrationFee": 2,
                "rewardFirst": 200,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "maxPlayers": 40,
            },
            {
                "categoryId": "b",
                "color": "#FFFF00",
                "minPoints": 800,
                "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                    "%Y-%m-%dT%H:%M:%S",
                ),
                "baseRegistrationFee": 20,
                "lateRegistrationFee": 4,
                "rewardFirst": 200,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "maxPlayers": 40,
            },
            {
                "categoryId": "c",
                "color": "#FFFFFF",
                "minPoints": 800,
                "maxPoints": 2000,
                "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                    "%Y-%m-%dT%H:%M:%S",
                ),
                "womenOnly": True,
                "baseRegistrationFee": 20,
                "lateRegistrationFee": 4,
                "rewardFirst": 200,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "maxPlayers": 40,
                "overbookingPercentage": 10,
            },
            {
                "categoryId": "d",
                "maxPoints": 1500,
                "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                    "%Y-%m-%dT%H:%M:%S",
                ),
                "baseRegistrationFee": 10,
                "lateRegistrationFee": 2,
                "rewardFirst": 200,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "maxPlayers": 40,
            },
        ],
    },
    {
        "categories": [
            {
                "alternateName": None,
                "baseRegistrationFee": 10,
                "categoryId": "a",
                "color": "#FF0000",
                "currentFee": 10,
                "entryCount": 0,
                "lateRegistrationFee": 2,
                "maxPlayers": 40,
                "maxPoints": 1500,
                "minPoints": 0,
                "overbookingPercentage": 0,
                "presentEntryCount": 0,
                "rewardFirst": 200,
                "rewardQuarter": None,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "startTime": "2023-12-20T10:00:00",
                "womenOnly": False,
            },
            {
                "alternateName": None,
                "baseRegistrationFee": 20,
                "categoryId": "b",
                "color": "#FFFF00",
                "currentFee": 20,
                "entryCount": 0,
                "lateRegistrationFee": 4,
                "maxPlayers": 40,
                "maxPoints": 4000,
                "minPoints": 800,
                "overbookingPercentage": 0,
                "presentEntryCount": 0,
                "rewardFirst": 200,
                "rewardQuarter": None,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "startTime": "2023-12-20T10:00:00",
                "womenOnly": False,
            },
            {
                "alternateName": None,
                "baseRegistrationFee": 20,
                "categoryId": "c",
                "color": "#FFFFFF",
                "currentFee": 20,
                "entryCount": 0,
                "lateRegistrationFee": 4,
                "maxPlayers": 40,
                "maxPoints": 2000,
                "minPoints": 800,
                "overbookingPercentage": 10,
                "presentEntryCount": 0,
                "rewardFirst": 200,
                "rewardQuarter": None,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "startTime": "2023-12-20T10:00:00",
                "womenOnly": True,
            },
            {
                "alternateName": None,
                "baseRegistrationFee": 10,
                "categoryId": "d",
                "color": None,
                "currentFee": 10,
                "entryCount": 0,
                "lateRegistrationFee": 2,
                "maxPlayers": 40,
                "maxPoints": 1500,
                "minPoints": 0,
                "overbookingPercentage": 0,
                "presentEntryCount": 0,
                "rewardFirst": 200,
                "rewardQuarter": None,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "startTime": "2023-12-20T10:00:00",
                "womenOnly": False,
            },
        ],
    },
)

correct_admin_set_categories = [correct_categories]

incorrect_set_categories_existing_entries = ae.RegistrationCutoffError(
    origin=origin,
    error_message=ae.REGISTRATION_MESSAGES["started"],
)

incorrect_categories_missing_categories_field = (
    {},
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.CATEGORY_FORMAT_MESSAGE,
        payload={"json": ["json payload should have 'categories' field."]},
    ),
)

incorrect_categories_missing_badly_formatted_data = (
    {
        "categories": [
            {
                "categoryId": "aa",
                "color": "#FF00000",
                "maxPoints": 1500,
                "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                    "%Y-%m-%dT%H:%M:%S",
                ),
                "rewardFirst": 200,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "maxPlayers": 40,
            },
            {
                "categoryId": "b",
                "color": "#FFFF00",
                "minPoints": 800,
                "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                    "%Y-%m-%dT%H:%M:%S",
                ),
                "baseRegistrationFee": 20,
                "lateRegistrationFee": 4,
                "rewardFirst": 200,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "maxPlayers": "aa",
            },
            {},
        ],
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.CATEGORY_FORMAT_MESSAGE,
        payload={
            "0": {
                "categoryId": ["Length must be 1."],
                "color": ["Length must be 7."],
                "baseRegistrationFee": ["Missing data for required field."],
                "lateRegistrationFee": ["Missing data for required field."],
            },
            "1": {"maxPlayers": ["Not a valid integer."]},
            "2": {
                "baseRegistrationFee": ["Missing data for required field."],
                "lateRegistrationFee": ["Missing data for required field."],
                "maxPlayers": ["Missing data for required field."],
                "rewardFirst": ["Missing data for required field."],
                "rewardSecond": ["Missing data for required field."],
                "rewardSemi": ["Missing data for required field."],
                "startTime": ["Missing data for required field."],
            },
        },
    ),
)

incorrect_categories_duplicate = (
    {
        "categories": [
            {
                "categoryId": "a",
                "color": "#FF0000",
                "maxPoints": 1500,
                "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                    "%Y-%m-%dT%H:%M:%S",
                ),
                "baseRegistrationFee": 10,
                "lateRegistrationFee": 2,
                "rewardFirst": 200,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "maxPlayers": 40,
            },
            {
                "categoryId": "a",
                "color": "#FFFF00",
                "minPoints": 800,
                "startTime": datetime(2023, 12, 20, 10, 00, 00).strftime(
                    "%Y-%m-%dT%H:%M:%S",
                ),
                "baseRegistrationFee": 20,
                "lateRegistrationFee": 4,
                "rewardFirst": 200,
                "rewardSecond": 100,
                "rewardSemi": 50,
                "maxPlayers": 40,
            },
        ],
    },
    ae.InvalidDataError(
        origin=origin,
        error_message=ae.CATEGORY_FORMAT_MESSAGE,
        payload={"category_ids": ["Different categories cannot have the same id"]},
    ),
)

incorrect_admin_set_categories = [
    incorrect_categories_missing_categories_field,
    incorrect_categories_missing_badly_formatted_data,
    incorrect_categories_duplicate,
]


class TestAPISetCategories(BaseTest):
    @pytest.mark.parametrize("payload,response", correct_admin_set_categories)
    def test_correct_admin_set_categories(self, client, reset_db, payload, response):
        r = client.post("/api/admin/categories", json=payload)
        assert r.status_code == HTTPStatus.CREATED, r.json
        assert r.json == response, r.json

    def test_incorrect_existing_entries(self, client, reset_db, populate):
        r = client.post("/api/admin/categories", json=correct_categories[0])
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == incorrect_set_categories_existing_entries.to_dict(), r.json

    @pytest.mark.parametrize("payload,error", incorrect_admin_set_categories)
    def test_incorrect_admin_set_categories(self, client, reset_db, payload, error):
        r = client.post("/api/admin/categories", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error.to_dict(), r.json
