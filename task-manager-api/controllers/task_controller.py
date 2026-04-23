from flask import jsonify, request

from services.task_service import TaskService


task_service = TaskService()


def get_tasks():
    return jsonify(task_service.get_tasks()), 200


def get_task(task_id):
    return jsonify(task_service.get_task(task_id)), 200


def create_task():
    return jsonify(task_service.create_task(request.get_json())), 201


def update_task(task_id):
    return jsonify(task_service.update_task(task_id, request.get_json())), 200


def delete_task(task_id):
    return jsonify(task_service.delete_task(task_id)), 200


def search_tasks():
    filters = {
        'q': request.args.get('q', ''),
        'status': request.args.get('status', ''),
        'priority': request.args.get('priority', ''),
        'user_id': request.args.get('user_id', ''),
    }
    return jsonify(task_service.search_tasks(filters)), 200


def task_stats():
    return jsonify(task_service.task_stats()), 200
