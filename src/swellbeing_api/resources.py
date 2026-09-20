import datetime

from flask import request
from flask_restful import Api, Resource, reqparse

from swellbeing_api.auth import require_token
from swellbeing_api.database import db
from swellbeing_api.models import User, WaterIntake


class HealthCheck(Resource):
    # noinspection method-may-be-static
    def get(self):
        return {"status": "ok"}

class UserList(Resource):
    @require_token
    def get(self):
        users = db.session.scalars(db.select(User).order_by(User.id)).all()
        return [user.to_dict() for user in users]

    @require_token
    def post(self):
        user = User()
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201


class UserResource(Resource):
    @require_token
    def get(self, id):
        user = db.get_or_404(User, id)
        return user.to_dict()

    @require_token
    def delete(self, id):
        user = db.session.scalars(db.select(User).filter(User.id == id)).first()
        if user is not None:
            db.session.delete(user)
            db.session.commit()
        return {}, 204


def parse_water_intake_time_range():
    parser = reqparse.RequestParser()
    parser.add_argument(
        "from", 
        type=datetime.datetime.fromisoformat, 
        help="Start time for the query",
        location="args", # Specify that the argument should be parsed from the query string
    )
    parser.add_argument(
        "to", 
        type=datetime.datetime.fromisoformat, 
        help="End time for the query",
        location="args", # Specify that the argument should be parsed from the query string
    )
    args = parser.parse_args()
    return args["from"], args["to"]


class WaterIntakeList(Resource):
    @require_token
    def get(self, user_id):
        from_time, to_time = parse_water_intake_time_range()
        query = (
            db.select(WaterIntake)
            .filter_by(user_id=user_id)
            .order_by(WaterIntake.timestamp)
        )
        if from_time is not None:
            query = query.filter(WaterIntake.timestamp >= from_time)
        if to_time is not None:
            query = query.filter(WaterIntake.timestamp <= to_time)
        water_intakes = db.session.scalars(query).all()
        return [intake.to_dict() for intake in water_intakes]

    @require_token
    def post(self, user_id):
        data = request.get_json()
        volume = data.get("volume")

        if volume is None:
            return {"error": "Volume is required"}, 400

        user = db.session.scalars(db.select(User).filter(User.id == user_id)).first()
        if user is None:
            return {"error": "User not found"}, 404

        water_intake = WaterIntake(user_id=user_id, volume=volume)
        db.session.add(water_intake)
        db.session.commit()
        return water_intake.to_dict(), 201


def register_resources(app):
    api = Api(app)
    api.add_resource(HealthCheck, "/health")
    api.add_resource(UserList, "/users")
    api.add_resource(UserResource, "/users/<uuid:id>")
    api.add_resource(WaterIntakeList, "/users/<uuid:user_id>/water_intakes")
