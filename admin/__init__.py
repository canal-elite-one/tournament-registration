from flask import Flask

from admin.api.admin import admin_api_bp
from admin.front.routes.admin import admin_bp
from shared.api.api_errors import handle_api_error, APIError
from shared import get_config


def create_app(debug=None):
    app = Flask(__name__)
    app.register_blueprint(admin_api_bp)
    app.register_blueprint(admin_bp)
    app.register_error_handler(APIError, handle_api_error)

    app.config.update(get_config())

    if debug is not None:
        app.config["DEBUG"] = debug

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
