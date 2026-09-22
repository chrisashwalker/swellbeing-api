import os

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def configure_database(app, *, testing):
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"postgresql://"
            f"{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@"
            f"{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/"
            f"{os.getenv('DATABASE_NAME')}"
        )
