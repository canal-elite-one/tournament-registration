from flask import Flask
from flaskr import api

app = Flask(__name__)

app.register_blueprint(api.bp)


@app.route('/')
def index():
    return 'test'


if __name__ == '__main__':
    app.run(debug=True, port=5000)
