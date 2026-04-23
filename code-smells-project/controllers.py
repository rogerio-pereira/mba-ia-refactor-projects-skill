from flask import request, jsonify
from errors import AppError
import auth_service
import health_service
import order_service
import product_repository
import report_service
import user_repository
from validators import (
    parse_busca_params,
    parse_json_payload,
    validate_login_payload,
    validate_pedido_payload,
    validate_produto_payload,
    validate_status_payload,
    validate_usuario_payload,
)

def listar_produtos():
    produtos = product_repository.get_todos_produtos()
    print("Listando " + str(len(produtos)) + " produtos")
    return jsonify({"dados": produtos, "sucesso": True}), 200

def buscar_produto(id):
    produto = product_repository.get_produto_por_id(id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    raise AppError("Produto não encontrado", 404)

def criar_produto():
    dados = validate_produto_payload(request.get_json(silent=True))
    produto_id = product_repository.criar_produto(**dados)
    print("Produto criado com ID: " + str(produto_id))
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201

def atualizar_produto(id):
    produto_existente = product_repository.get_produto_por_id(id)
    if not produto_existente:
        raise AppError("Produto não encontrado", 404)

    dados = validate_produto_payload(request.get_json(silent=True))
    product_repository.atualizar_produto(id, **dados)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

def deletar_produto(id):
    produto = product_repository.get_produto_por_id(id)
    if not produto:
        raise AppError("Produto não encontrado", 404)

    product_repository.deletar_produto(id)
    print("Produto " + str(id) + " deletado")
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200

def buscar_produtos():
    filtros = parse_busca_params(request.args)
    resultados = product_repository.buscar_produtos(**filtros)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200

def listar_usuarios():
    usuarios = user_repository.get_todos_usuarios()
    return jsonify({"dados": usuarios, "sucesso": True}), 200

def buscar_usuario(id):
    usuario = user_repository.get_usuario_por_id(id)
    if usuario:
        return jsonify({"dados": usuario, "sucesso": True}), 200
    raise AppError("Usuário não encontrado", 404)

def criar_usuario():
    dados = validate_usuario_payload(request.get_json(silent=True))
    usuario_id = auth_service.criar_usuario(**dados)
    print("Usuário criado: " + dados["email"])
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201

def login():
    dados = validate_login_payload(request.get_json(silent=True))
    usuario = auth_service.login_usuario(dados["email"], dados["senha"])
    if usuario:
        print("Login bem-sucedido: " + dados["email"])
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200

    print("Login falhou: " + dados["email"])
    raise AppError("Email ou senha inválidos", 401)

def criar_pedido():
    dados = validate_pedido_payload(request.get_json(silent=True))
    resultado = order_service.criar_pedido(dados["usuario_id"], dados["itens"])

    if "erro" in resultado:
        raise AppError(resultado["erro"], 400)

    return jsonify({
        "dados": resultado,
        "sucesso": True,
        "mensagem": "Pedido criado com sucesso"
    }), 201

def listar_pedidos_usuario(usuario_id):
    pedidos = order_service.get_pedidos_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200

def listar_todos_pedidos():
    pedidos = order_service.get_todos_pedidos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200

def atualizar_status_pedido(pedido_id):
    novo_status = validate_status_payload(request.get_json(silent=True))
    order_service.atualizar_status_pedido(pedido_id, novo_status)

    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200

def relatorio_vendas():
    relatorio = report_service.relatorio_vendas()
    return jsonify({"dados": relatorio, "sucesso": True}), 200

def health_check():
    return jsonify(health_service.get_health_status()), 200
