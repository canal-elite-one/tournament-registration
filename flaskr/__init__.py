from flask import Flask
from flaskr import api


def create_app(cfg_filename=None):
    app = Flask(__name__)
    # app.config.from_pyfile(cfg_filename)
    app.register_blueprint(api.bp)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
