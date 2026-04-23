from flask import jsonify, request

from services.category_service import CategoryService
from services.report_service import ReportService


report_service = ReportService()
category_service = CategoryService()


def summary_report():
    return jsonify(report_service.summary_report()), 200


def user_report(user_id):
    response, status_code = report_service.user_report(user_id)
    return jsonify(response), status_code


def get_categories():
    return jsonify(category_service.get_categories()), 200


def create_category():
    response, status_code = category_service.create_category(request.get_json())
    return jsonify(response), status_code


def update_category(cat_id):
    response, status_code = category_service.update_category(cat_id, request.get_json())
    return jsonify(response), status_code


def delete_category(cat_id):
    response, status_code = category_service.delete_category(cat_id)
    return jsonify(response), status_code
