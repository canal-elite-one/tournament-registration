from flask import Flask
from flaskr.api import api_bp
from flaskr.front.routes.public import public_bp
from flaskr.front.routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
