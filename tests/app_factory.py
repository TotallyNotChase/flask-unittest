from example.flaskr import create_app
from example.flaskr.db import init_db


def build_app():
    # Create and set up the app
    # Do all the app config + pre launch setup here
    app = create_app({'TESTING': True})
    # Set up the database - this also drops existing tables
    with app.app_context():
        init_db()
    return app
