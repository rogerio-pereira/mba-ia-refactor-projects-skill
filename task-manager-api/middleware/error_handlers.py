import logging

from flask import jsonify

from errors import ApiError


def register_error_handlers(app):
    logger = logging.getLogger(__name__)

    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception('Unhandled application error', exc_info=error)
        return jsonify({'error': 'Erro interno'}), 500
