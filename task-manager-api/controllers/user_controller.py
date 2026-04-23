from flask import jsonify, request

from services.user_service import UserService


user_service = UserService()


def get_users():
    return jsonify(user_service.get_users()), 200


def get_user(user_id):
    response, status_code = user_service.get_user(user_id)
    return jsonify(response), status_code


def create_user():
    response, status_code = user_service.create_user(request.get_json())
    return jsonify(response), status_code


def update_user(user_id):
    response, status_code = user_service.update_user(user_id, request.get_json())
    return jsonify(response), status_code


def delete_user(user_id):
    response, status_code = user_service.delete_user(user_id)
    return jsonify(response), status_code


def get_user_tasks(user_id):
    response, status_code = user_service.get_user_tasks(user_id)
    return jsonify(response), status_code


def login():
    response, status_code = user_service.login(request.get_json())
    return jsonify(response), status_code
