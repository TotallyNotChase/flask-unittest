from tests.flaskr import create_app
from tests.flaskr.db import init_db

# Create and set up the app
# Do all the app config + pre launch setup here
app = create_app()
app.testing = True
# Set up the database - this also drops existing tables
with app.app_context():
    init_db()
