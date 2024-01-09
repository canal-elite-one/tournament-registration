from flask import Flask
from flaskr.api.admin import admin_api_bp
from flaskr.api.public import public_api_bp
from flaskr.front.routes.public import public_bp, not_found_page
from flaskr.front.routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(admin_api_bp)
    app.register_blueprint(public_api_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    app.register_error_handler(404, not_found_page)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
