from tests.flaskr import create_app

# Create and set up the app
# Do all the app config + pre launch setup here
app = create_app()
app.testing = True