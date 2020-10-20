from flask import (
    Flask,
    Response,
)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super secret testing key'
    app.testing = True

    @app.route("/")
    def index():
        return Response("OK")

    return app
