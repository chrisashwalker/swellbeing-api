import os

from flask import Flask
from flask_migrate import Migrate

from swellbeing_api.database import configure_database, db
from swellbeing_api.resources import register_resources


def create_app(*, testing=None):
    if testing is None:
        testing = os.getenv("TESTING", "False").lower() == "true"

    flask_app = Flask(__name__)
    configure_database(flask_app, testing=testing)
    db.init_app(flask_app)

    if testing:
        with flask_app.app_context():
            db.create_all()

    register_resources(flask_app)
    return flask_app


app = create_app()
Migrate(app, db)
