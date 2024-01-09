from conftest import BaseTest
from http import HTTPStatus


correct_admin_reset_all_bibs = {"confirmation": "Je suis sur! J'ai appelé Céline!"}


class TestAPIResetBibNos(BaseTest):
    def test_correct_reset_all_bibs(self, client, reset_db, populate, set_a_few_bibs):
        r = client.delete("/api/admin/bibs", json=correct_admin_reset_all_bibs)
        assert r.status_code == HTTPStatus.NO_CONTENT

    def test_incorrect_reset_all_bibs(self, client, reset_db, populate, set_a_few_bibs):
        r = client.delete("/api/admin/bibs", json={"confirmation": ""})
        assert r.status_code == HTTPStatus.FORBIDDEN
