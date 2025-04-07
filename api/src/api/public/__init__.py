from flask import Flask, redirect, url_for

from api.public.api import public_api_bp
from api.public.front import public_bp, not_found_page
from api.shared.api.api_errors import handle_api_error, APIError
from api.shared import get_config_from_env


def create_app(debug=None):
    app = Flask(__name__)
    app.register_blueprint(public_api_bp)
    app.register_blueprint(public_bp)
    app.register_error_handler(404, not_found_page)
    app.register_error_handler(APIError, handle_api_error)

    @app.route("/", methods=["GET"])
    def index_page():
        return redirect(url_for("public.index_page"))

    app.config.update(get_config_from_env())

    if debug is not None:
        app.config["DEBUG"] = debug

    return app


def main(debug=None):
    app = create_app(debug)
    app.run()


if __name__ == "__main__":
    main()
