import os
from datetime import datetime

from flask import Flask

from admin.api.admin import admin_api_bp
from admin.front.routes.admin import admin_bp
from shared.api.api_errors import handle_api_error, APIError


def create_app(debug=False):
    app = Flask(__name__)
    app.register_blueprint(admin_api_bp)
    app.register_blueprint(admin_bp)
    app.register_error_handler(APIError, handle_api_error)

    app.config["TOURNAMENT_REGISTRATION_CUTOFF"] = datetime.fromisoformat(
        os.environ.get("TOURNAMENT_REGISTRATION_CUTOFF"),
    )
    app.config["MAX_ENTRIES_PER_DAY"] = int(os.environ.get("MAX_ENTRIES_PER_DAY", 3))

    app.config["DEBUG"] = debug
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
