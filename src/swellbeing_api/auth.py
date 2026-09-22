import os
from functools import wraps

from flask import request

ACCESS_TOKENS = os.getenv("ACCESS_TOKENS", "").split(",")


def is_valid_token(token):
    return token in ACCESS_TOKENS


def require_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        header = request.headers.get("Authorization", "")

        scheme, _, token = header.partition(" ")

        if scheme.lower() != "bearer" or not token:
            return {"error": "Invalid auth header"}, 401

        if not is_valid_token(token):
            return {"error": "Invalid auth token"}, 401

        return func(*args, **kwargs)

    return wrapped
