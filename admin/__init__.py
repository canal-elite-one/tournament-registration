from flask import Flask, redirect, url_for

from admin.api import api_bp
from admin.front import front_bp
from shared.api.api_errors import handle_api_error, APIError
from shared import get_config_from_env


def create_app(debug=None):
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    app.register_blueprint(front_bp)
    app.register_error_handler(APIError, handle_api_error)

    @app.route("/", methods=["GET"])
    def index_page():
        return redirect(url_for("admin.index"))

    app.config.update(get_config_from_env())

    if debug is not None:
        app.config["DEBUG"] = debug

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
