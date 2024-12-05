from typing import Tuple
from flask import Blueprint, Response, current_app, request
from flask_cors import CORS, cross_origin
from sqlalchemy import null
from sqlalchemy.exc import IntegrityError

from app.main.model.user import User
from app.main.service import user_service
from app.main.service.user_service import UserService
from app.main.controller.defaults import *

user_bp = Blueprint('user', __name__)
CORS(user_bp)

@cross_origin()
@user_bp.route('/create', methods=['POST', 'OPTIONS'])
def create_user() -> Tuple[Response, int]:
    print(request)
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return ret_400()

    with current_app.app_context():
        user_service: UserService = current_app.extensions['user_service']
        try:
            user = user_service.create_user(username, password)
        except (IntegrityError, FileExistsError):
            return ret_409()
        return jsonify({"message": "SUCCESS", "accessToken": user.access_token}), 200
    return ret_500()

@cross_origin()
@user_bp.route('/get_token', methods=['POST'])
def get_token() -> Tuple[Response, int]:
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return ret_400()

    with current_app.app_context():
        user_service: UserService = current_app.extensions['user_service']
        token = user_service.get_token(username, password)
        if token is None:
            return ret_401()
        return jsonify({"message": "SUCCESS", "accessToken": token}), 200
    return ret_500()

@cross_origin()
@user_bp.route('/delete', methods=['DELETE'])
def delete_user() -> Tuple[Response, int]:
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        return ret_400()

    with current_app.app_context():
        user_service: UserService = current_app.extensions['user_service']
        try:
            user_service.delete_user(token)
            return ret_200()
        except Exception as e:
            print(e)
            return ret_500()
    return ret_500()

@cross_origin()
@user_bp.route('/get', methods=['POST'])
def get_user() -> Tuple[Response, int]:
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        return ret_400()

    with current_app.app_context():
        user_service: UserService = current_app.extensions['user_service']
        try:
            user = user_service.find_by_token(token)
            if user is None:
                return ret_401()
            return jsonify({"username": user.username, "accessToken": user.access_token}), 200
        except Exception as e:
            current_app.logger.error(e)
            return ret_500()




