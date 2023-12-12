from conftest import BaseTest
from http import HTTPStatus
import pytest
import tests.testing_data.api_data as td


class TestAPISetCategories(BaseTest):
    @pytest.mark.parametrize("payload,response", td.correct_admin_set_categories)
    def test_correct_admin_set_categories(self, client, reset_db, payload, response):
        r = client.post("/api/categories", json=payload)
        assert r.status_code == HTTPStatus.CREATED, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize("payload,error", td.incorrect_admin_set_categories)
    def test_incorrect_admin_set_categories(self, client, reset_db, payload, error):
        r = client.post("/api/categories", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json


class TestAPIMakePayment(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,payload,response",
        td.correct_admin_make_payment,
    )
    def test_correct_admin_make_payment(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        response,
    ):
        r = client.put(f"/api/pay/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize(
        "licence_no,payload,error",
        td.incorrect_admin_make_payment,
    )
    def test_incorrect_admin_make_payment(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        error,
    ):
        r = client.put(f"/api/pay/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json


class TestAPIDeleteEntries(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,payload,response",
        td.correct_admin_delete_entries,
    )
    def test_correct_admin_delete_entries(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        response,
    ):
        r = client.delete(f"/api/entries/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize(
        "licence_no,payload,error",
        td.incorrect_admin_delete_entries,
    )
    def test_incorrect_admin_delete_entries(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        error,
    ):
        r = client.delete(f"/api/entries/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json


class TestAPIDeletePlayer(BaseTest):
    def test_correct_admin_delete_player(self, client, reset_db, populate):
        r = client.delete(f"/api/players/{td.overall_correct_licence}")
        assert r.status_code == HTTPStatus.NO_CONTENT, r.json

    def test_incorrect_admin_delete_player(
        self,
        client,
        reset_db,
        populate,
    ):
        r = client.delete(f"/api/players/{td.overall_incorrect_licence}")
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == td.get_player_not_found_error(
            td.overall_incorrect_licence,
        ), r.json


class TestAPIMarkPresent(BaseTest):
    @pytest.mark.parametrize(
        "licence_no,payload,response",
        td.correct_admin_mark_present,
    )
    def test_correct_admin_mark_present(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        response,
    ):
        r = client.put(f"/api/present/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize(
        "licence_no,payload,error",
        td.incorrect_admin_mark_present,
    )
    def test_incorrect_admin_mark_present(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        error,
    ):
        r = client.put(f"/api/present/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json


class TestAPIAssignAllBibNos(BaseTest):
    def test_correct_assign_all(self, client, reset_db, populate):
        r = client.post("/api/bibs")
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == td.correct_admin_assign_all_response

    def test_incorrect_assign_all(self, client, reset_db, populate, set_a_few_bibs):
        r = client.post("/api/bibs")
        assert r.status_code == HTTPStatus.CONFLICT, r.json
        assert r.json == td.incorrect_admin_assign_all_already_assigned_error, r.json


class TestAPIAssignOneBibNo(BaseTest):
    def test_correct_assign_one(self, client, reset_db, populate, set_a_few_bibs):
        r = client.put(f"/api/bibs/{td.correct_admin_assign_one}")
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == td.correct_assign_one_response, r.json

    def test_incorrect_assign_one_without_any_assigned(
        self,
        client,
        reset_db,
        populate,
    ):
        r = client.put(f"/api/bibs/{td.correct_admin_assign_one}")
        assert r.status_code == HTTPStatus.CONFLICT, r.json
        assert (
            r.json == td.incorrect_admin_assign_one_without_any_assigned_error
        ), r.json

    @pytest.mark.parametrize(
        "licence_no,error,status_code",
        td.incorrect_admin_assign_one,
    )
    def test_incorrect_assign_one(
        self,
        client,
        reset_db,
        populate,
        set_a_few_bibs,
        licence_no,
        error,
        status_code,
    ):
        r = client.put(f"/api/bibs/{licence_no}")
        assert r.status_code == status_code, r.json
        assert r.json == error, r.json


class TestAPIResetBibNos(BaseTest):
    def test_correct_reset_all_bibs(self, client, reset_db, populate, set_a_few_bibs):
        r = client.delete("/api/bibs", json=td.correct_admin_reset_all_bibs)
        assert r.status_code == HTTPStatus.NO_CONTENT

    def test_incorrect_reset_all_bibs(self, client, reset_db, populate, set_a_few_bibs):
        r = client.delete("/api/bibs", json={"confirmation": ""})
        assert r.status_code == HTTPStatus.FORBIDDEN


class TestAPIGetPlayersByCategories(BaseTest):
    def test_admin_get_by_cat(self, client, reset_db, populate):
        r = client.get("/api/by_category?present_only=false")
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == td.correct_admin_get_by_cat_response, r.json

    def test_admin_get_by_cat_present_only(self, client, reset_db, populate):
        r = client.get("/api/by_category?present_only=true")
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == td.correct_admin_get_by_cat_present_only_response, r.json


class TestAPIGetAllPlayers(BaseTest):
    def test_admin_get_all_players(self, client, reset_db, populate):
        r = client.get("/api/all_players?present_only=false")
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == td.correct_admin_get_all_players_response, r.json

    def test_admin_get_all_players_present_only(self, client, reset_db, populate):
        r = client.get("/api/all_players?present_only=true")
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == td.correct_admin_get_all_players_present_only_response, r.json


class TestAPIGetCategories(BaseTest):
    def test_get(self, client, reset_db, populate):
        r = client.get("/api/categories")
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == td.correct_get_categories_response, r.json


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
        assert r.json == error, r.json


class TestGetPlayer(BaseTest):
    @pytest.mark.parametrize("licence_no,response", td.correct_get_player)
    def test_correct_get_player(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        response,
    ):
        r = client.get(f"/api/players/{licence_no}")
        assert r.status_code == HTTPStatus.OK, r.json
        assert r.json == response, r.json

    @pytest.mark.parametrize("licence_no,error", td.incorrect_get_player)
    def test_incorrect_get_player(self, client, reset_db, populate, licence_no, error):
        r = client.get(f"/api/players/{licence_no}")
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json


class TestRegisterEntries(BaseTest):
    @pytest.mark.parametrize("licence_no,payload,response", td.correct_register_entries)
    def test_correct_register_entries(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        response,
    ):
        r = client.post(f"/api/entries/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.CREATED, r.json
        assert "registeredEntries" in r.json, r.json
        for entry1, entry2 in zip(response, r.json["registeredEntries"]):
            for key in entry1:
                assert entry1[key] == entry2[key] or (
                    key == "registrationTime" and entry2["categoryId"] == "1"
                ), r.json
        for entry1, entry2 in zip(r.json["registeredEntries"], response):
            for key in entry1:
                assert entry1[key] == entry2[key] or (
                    key == "registrationTime" and entry2["categoryId"] == "1"
                ), r.json

    @pytest.mark.parametrize("licence_no,payload,error", td.incorrect_register_entries)
    def test_incorrect_register_entries(
        self,
        client,
        reset_db,
        populate,
        licence_no,
        payload,
        error,
    ):
        r = client.post(f"/api/entries/{licence_no}", json=payload)
        assert r.status_code == HTTPStatus.BAD_REQUEST, r.json
        assert r.json == error, r.json
