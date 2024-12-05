from typing import Tuple
from flask import Response, jsonify


def ret_404() -> Tuple[Response, int]:
    return jsonify({"error": "NOT_FOUND"}), 404

def ret_400() -> Tuple[Response, int]:
    return jsonify({"error": "BAD_REQUEST"}), 400

def ret_401() -> Tuple[Response, int]:
    return jsonify({"error": "UNAUTHORIZED"}), 401

def ret_405() -> Tuple[Response, int]:
    return jsonify({"error": "METHOD_NOT_ALLOWED"}), 405

def ret_409() -> Tuple[Response, int]:
    return jsonify({"error": "CONFLICT"}), 409

def ret_500() -> Tuple[Response, int]:
    return jsonify({"error": "INTERNAL_SERVER_ERROR"}), 500

def ret_200() -> Tuple[Response, int]:
    return jsonify({"message": "SUCCESS"}), 200
