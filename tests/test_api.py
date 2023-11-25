from testing_data import correct_category_dicts, incorrect_category_dicts
import requests

test_url = "http://localhost:5000"
api_test_url = test_url + "/api"


class TestAPISetCategories:
    def test_correct(self):
        r = requests.post(api_test_url + "/categories", json=correct_category_dicts)
        assert r.status_code // 100 == 2

    def test_incorrect(self):
        r = requests.post(api_test_url + "/categories", json=incorrect_category_dicts)
        assert r.status_code // 100 == 4


class TestAPIGetCategories:
    def test_get(self):
        r = requests.get(api_test_url + "/categories")
        assert r.status_code // 100 == 2
        payload = r.json()
        assert isinstance(payload, list)
        assert isinstance((payload or [{}])[0], dict)
