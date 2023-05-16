from functools import wraps

import jwt
from flask import jsonify, request

from config import app_config


def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app_config.SECRET_KEY)
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return func(*args, **kwargs)

    return jwt_required_wrapper

