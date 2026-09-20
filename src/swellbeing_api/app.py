import os

from flask import Flask

from swellbeing_api.database import configure_database, db
from swellbeing_api.resources import register_resources


def create_app(*, testing=None):
    if testing is None:
        testing = os.getenv("TESTING", "False").lower() == "true"

    app = Flask(__name__)
    configure_database(app, testing=testing)
    db.init_app(app)

    with app.app_context():
        db.create_all()  # TODO: Use migrations instead of create_all in production

    register_resources(app)
    return app


app = create_app()
