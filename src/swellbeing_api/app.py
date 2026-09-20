import datetime
import os
import uuid

from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass

app = Flask(__name__)
api = Api(app)

testing = os.getenv('TESTING', 'False').lower() == 'true'

if testing:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {
            "check_same_thread": False,
        },
        "poolclass": StaticPool,
    }
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{os.getenv("DATABASE_USER")}:{os.getenv("DATABASE_PASSWORD")}@{os.getenv("DATABASE_HOST")}:{os.getenv("DATABASE_PORT")}/{os.getenv("DATABASE_NAME")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(model_class=Base)

class User(db.Model):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)

class WaterIntake(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(db.ForeignKey('user.id'), nullable=False)
    volume: Mapped[float] = mapped_column(db.Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.datetime.now(tz=datetime.UTC))

with app.app_context():
    db.init_app(app)
    db.create_all() # TODO: Use migrations instead of create_all in production

class UserList(Resource):
    def get(self):
        users = db.session.execute(db.select(User).order_by(User.id)).scalars().all()
        return [{'id': str(user.id)} for user in users]

    def post(self):
        user = User()
        db.session.add(user)
        db.session.commit()
        return {'id': str(user.id)}, 201

class UserResource(Resource):
    def get(self, id):
        user = db.get_or_404(User, id)
        return {'id': str(user.id)}

    def delete(self, id):
        user = db.get_or_404(User, id)
        db.session.delete(user)
        db.session.commit()
        return {}, 204

api.add_resource(UserList, '/users')
api.add_resource(UserResource, '/users/<uuid:id>')

class HealthCheck(Resource):
    def get(self):
        return {'status': 'ok'}

api.add_resource(HealthCheck, '/health')    

class WaterIntakeList(Resource):
    def get(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('from', type=datetime.datetime.fromisoformat, help='Start time for the query')
        parser.add_argument('to', type=datetime.datetime.fromisoformat, help='End time for the query')
        args = parser.parse_args()
        from_time = args.get('from', 0)
        to_time = args.get('to', datetime.datetime.now(tz=datetime.UTC))

        water_intakes = db.session.execute(db.select(WaterIntake).filter_by(user_id=user_id).filter(WaterIntake.timestamp >= from_time, WaterIntake.timestamp <= to_time).order_by(WaterIntake.timestamp)).scalars().all()

        return [{'id': intake.id, 'user_id': intake.user_id, 'volume': intake.volume, 'timestamp': intake.timestamp.isoformat()} for intake in water_intakes]

    def post(self, user_id):
        data = request.get_json()
        volume = data.get('volume')

        if volume is None:
            return {'error': 'Volume is required'}, 400

        db.get_or_404(User, user_id)

        water_intake = WaterIntake(user_id=user_id, volume=volume)
        db.session.add(water_intake)
        db.session.commit()
        return {'id': water_intake.id}, 201

api.add_resource(WaterIntakeList, '/users/<uuid:user_id>/water_intakes')
