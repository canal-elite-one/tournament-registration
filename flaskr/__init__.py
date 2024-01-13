import os
from datetime import datetime

from flask import Flask

from flaskr.api.admin import admin_api_bp
from flaskr.api.public import public_api_bp
from flaskr.front.routes.public import public_bp, not_found_page
from flaskr.front.routes.admin import admin_bp
from flaskr.api.api_errors import handle_api_error, APIError


def create_app(debug=False):
    app = Flask(__name__)
    app.register_blueprint(admin_api_bp)
    app.register_blueprint(public_api_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_error_handler(404, not_found_page)
    app.register_error_handler(APIError, handle_api_error)

    app.config["TOURNAMENT_REGISTRATION_CUTOFF"] = datetime.fromisoformat(
        os.environ.get("TOURNAMENT_REGISTRATION_CUTOFF"),
    )
    app.config["MAX_ENTRIES_PER_DAY"] = int(os.environ.get("MAX_ENTRIES_PER_DAY", 3))

    app.config["DEBUG"] = debug
    return app


if __name__ == "__main__":
    # with freeze_time("2021-01-01"):
    #     app = create_app()
    #     app.run(debug=True)
    app = create_app()
    app.run(debug=True)
