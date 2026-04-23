import logging
from flask import current_app, has_app_context


def _get_logger():
    if has_app_context():
        return current_app.logger
    return logging.getLogger(__name__)


def notificar_pedido_criado(pedido_id, usuario_id):
    logger = _get_logger()
    logger.info("Enviando notificacoes de criacao para pedido %s do usuario %s", pedido_id, usuario_id)


def notificar_status_pedido(pedido_id, novo_status):
    logger = _get_logger()
    if novo_status == "aprovado":
        logger.info("Pedido %s aprovado; preparar envio", pedido_id)
    if novo_status == "cancelado":
        logger.info("Pedido %s cancelado; devolver estoque", pedido_id)
