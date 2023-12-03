from conftest import BaseTest
from http import HTTPStatus
import pytest
import tests.testing_data as td


class TestAPISetCategories(BaseTest):
    @pytest.mark.parametrize("payload,response", td.correct_admin_set_categories)
    def test_correct_admin_set_categories(self, client, reset_db, payload, response):
        r = client.post("/api/categories", json=payload)
        assert r.status_code == HTTPStatus.CREATED, r.json
        assert "categories" in r.json
        assert r.json["categories"] == response, r.json

    @pytest.mark.parametrize("payload,error", td.incorrect_admin_set_categories)
    def test_incorrect_admin_set_categories(self, client, reset_db, payload, error):
        r = client.post("/api/categories", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert "error" in r.json, r.json
        assert error in r.json["error"], r.json


class TestAPIMakePayment(BaseTest):
    @pytest.mark.parametrize("payload,response", td.correct_admin_make_payment)
    def test_correct_admin_make_payment(
        self,
        client,
        reset_db,
        populate,
        payload,
        response,
    ):
        r = client.put("/api/pay", json=payload)
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize("payload,error", td.incorrect_admin_make_payment)
    def test_incorrect_admin_make_payment(
        self,
        client,
        reset_db,
        populate,
        payload,
        error,
    ):
        r = client.put("/api/pay", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert "error" in r.json, r.json
        assert error in r.json["error"], r.json


class TestAPIDeleteEntries(BaseTest):
    @pytest.mark.parametrize("payload,response", td.correct_admin_delete_entries)
    def test_correct_admin_delete_entries(
        self,
        client,
        reset_db,
        populate,
        payload,
        response,
    ):
        r = client.delete("/api/entries", json=payload)
        assert r.status_code == HTTPStatus.OK, r.json
        assert "remainingEntries" in r.json, r.json
        assert r.json["remainingEntries"] == response, r.json

    @pytest.mark.parametrize("payload,error", td.incorrect_admin_delete_entries)
    def test_incorrect_admin_delete_entries(
        self,
        client,
        reset_db,
        populate,
        payload,
        error,
    ):
        r = client.delete("/api/entries", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert "error" in r.json, r.json
        assert error in r.json["error"], r.json


class TestAPIDeletePlayer(BaseTest):
    @pytest.mark.parametrize("payload", td.correct_admin_delete_player)
    def test_correct_admin_delete_player(self, client, reset_db, populate, payload):
        r = client.delete("/api/players", json=payload)
        assert r.status_code == HTTPStatus.NO_CONTENT, r.json

    @pytest.mark.parametrize("payload, error", td.incorrect_admin_delete_player)
    def test_incorrect_admin_delete_player(
        self,
        client,
        reset_db,
        populate,
        payload,
        error,
    ):
        r = client.delete("/api/players", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert "error" in r.json, r.json
        assert error in r.json["error"], r.json


class TestAPIMarkPresent(BaseTest):
    @pytest.mark.parametrize("payload,response", td.correct_admin_mark_present)
    def test_correct_admin_mark_present(
        self,
        client,
        reset_db,
        populate,
        payload,
        response,
    ):
        r = client.put("/api/present", json=payload)
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize("payload,error", td.incorrect_admin_mark_present)
    def test_incorrect_admin_mark_present(
        self,
        client,
        reset_db,
        populate,
        payload,
        error,
    ):
        r = client.put("/api/present", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert "error" in r.json, r.json
        assert error in r.json["error"], r.json


class TestAPIGetCategories(BaseTest):
    def test_get(self, client, reset_db, populate):
        r = client.get("/api/categories")
        assert r.status_code == HTTPStatus.OK, r.json
        assert "categories" in r.json, r.json
        assert r.json["categories"] == td.correct_get_categories_response


class TestAPIAddPlayer(BaseTest):
    @pytest.mark.parametrize("payload,response", td.correct_add_player)
    def test_correct_add_player(self, client, reset_db, populate, payload, response):
        r = client.post("/api/players", json=payload)
        assert r.status_code == HTTPStatus.CREATED, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize("payload, error", td.incorrect_add_player)
    def test_incorrect_add_player(self, client, reset_db, populate, payload, error):
        r = client.post("/api/players", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert "error" in r.json, r.json
        assert error in r.json["error"], r.json


class TestGetPlayerInfo(BaseTest):
    @pytest.mark.parametrize("payload,response", td.correct_get_player)
    def test_correct_existing_player(
        self,
        client,
        reset_db,
        populate,
        payload,
        response,
    ):
        r = client.get("/api/players", json=payload)
        assert r.status_code == HTTPStatus.OK, r.json
        assert "player" in r.json, r.json
        assert r.json["player"] == response["player"], r.json
        assert "registeredEntries" in r.json, r.json
        assert r.json["registeredEntries"] == response["registeredEntries"], r.json

    @pytest.mark.parametrize("payload, error", td.incorrect_get_player)
    def test_incorrect_missing_field(self, client, reset_db, populate, payload, error):
        r = client.get("/api/players", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert "error" in r.json, r.json
        assert error in r.json["error"], r.json


class TestRegisterEntries(BaseTest):
    @pytest.mark.parametrize("payload,response", td.correct_register_entries)
    def test_correct_register_entries(
        self,
        client,
        reset_db,
        populate,
        payload,
        response,
    ):
        r = client.post("/api/entries", json=payload)
        assert r.status_code == HTTPStatus.CREATED, r.json
        assert "entries" in r.json, r.json
        for entry1, entry2 in zip(r.json["entries"], response):
            for key in entry1:
                assert entry1[key] == entry2[key] or (
                    key == "registrationTime" and entry1["categoryId"] == "1"
                ), r.json

    @pytest.mark.parametrize("payload, error", td.incorrect_register_entries)
    def test_incorrect_register_entries(
        self,
        client,
        reset_db,
        populate,
        payload,
        error,
    ):
        r = client.post("/api/entries", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert "error" in r.json, r.json
        assert error in r.json["error"], r.json
