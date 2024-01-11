from tests.conftest import BaseTest, before_cutoff, after_cutoff
from http import HTTPStatus

from freezegun import freeze_time


import flaskr.api.api_errors as ae

origin = "api_admin_reset_bibs"

confirmation = {"confirmation": ae.RESET_BIBS_CONFIRMATION}


class TestAPIResetBibNos(BaseTest):
    def test_correct_reset_all_bibs(self, client, reset_db, populate, set_a_few_bibs):
        with freeze_time(after_cutoff):
            r = client.delete("/api/admin/bibs", json=confirmation)
            assert r.status_code == HTTPStatus.NO_CONTENT

    def test_incorrect_confirmation_error(
        self,
        client,
        reset_db,
        populate,
        set_a_few_bibs,
    ):
        error = ae.ConfirmationError(
            origin=origin,
            error_message=ae.RESET_BIBS_CONFIRMATION_MESSAGE,
        )
        with freeze_time(after_cutoff):
            r = client.delete("/api/admin/bibs", json={"confirmation": "wrong"})
            assert r.status_code == error.status_code
            assert r.json == error.to_dict()

    def test_incorrect_before(self, client, reset_db, populate, set_a_few_bibs):
        with freeze_time(before_cutoff):
            r = client.delete("/api/admin/bibs", json=confirmation)
            assert r.status_code == ae.RegistrationCutoffError.status_code
            assert (
                r.json
                == ae.RegistrationCutoffError(
                    origin=origin,
                    error_message=ae.REGISTRATION_MESSAGES["not_ended"],
                ).to_dict()
            )
