from constants import VALID_CATEGORIES, VALID_ORDER_STATUSES
from errors import AppError


def _normalize_text(value):
    if not isinstance(value, str):
        return ""
    return value.strip()


def _require_dict(data):
    if not isinstance(data, dict):
        raise AppError("Dados inválidos", 400)
    return data


def parse_json_payload(data):
    return _require_dict(data)


def validate_produto_payload(data):
    data = _require_dict(data)

    if "nome" not in data:
        raise AppError("Nome é obrigatório", 400)
    if "preco" not in data:
        raise AppError("Preço é obrigatório", 400)
    if "estoque" not in data:
        raise AppError("Estoque é obrigatório", 400)

    nome = data["nome"]
    descricao = data.get("descricao", "")
    preco = data["preco"]
    estoque = data["estoque"]
    categoria = data.get("categoria", "geral")

    if preco < 0:
        raise AppError("Preço não pode ser negativo", 400)
    if estoque < 0:
        raise AppError("Estoque não pode ser negativo", 400)
    if len(nome) < 2:
        raise AppError("Nome muito curto", 400)
    if len(nome) > 200:
        raise AppError("Nome muito longo", 400)
    if categoria not in VALID_CATEGORIES:
        raise AppError("Categoria inválida. Válidas: " + str(VALID_CATEGORIES), 400)

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validate_usuario_payload(data):
    data = _require_dict(data)

    nome = _normalize_text(data.get("nome", ""))
    email = _normalize_text(data.get("email", "")).lower()
    senha = _normalize_text(data.get("senha", ""))

    if not nome or not email or not senha:
        raise AppError("Nome, email e senha são obrigatórios", 400)
    if "@" not in email or "." not in email.split("@")[-1]:
        raise AppError("Email inválido", 400)

    return {"nome": nome, "email": email, "senha": senha}


def validate_login_payload(data):
    data = _require_dict(data)

    email = _normalize_text(data.get("email", "")).lower()
    senha = _normalize_text(data.get("senha", ""))
    if not email or not senha:
        raise AppError("Email e senha são obrigatórios", 400)

    return {"email": email, "senha": senha}


def validate_pedido_payload(data):
    data = _require_dict(data)

    usuario_id = data.get("usuario_id")
    itens = data.get("itens", [])
    if not usuario_id:
        raise AppError("Usuario ID é obrigatório", 400)
    if not itens:
        raise AppError("Pedido deve ter pelo menos 1 item", 400)

    return {"usuario_id": usuario_id, "itens": itens}


def validate_status_payload(data):
    data = _require_dict(data)
    novo_status = data.get("status", "")

    if novo_status not in VALID_ORDER_STATUSES:
        raise AppError("Status inválido", 400)

    return novo_status


def parse_busca_params(args):
    try:
        preco_min = args.get("preco_min")
        preco_max = args.get("preco_max")
        return {
            "termo": args.get("q", ""),
            "categoria": args.get("categoria"),
            "preco_min": float(preco_min) if preco_min is not None else None,
            "preco_max": float(preco_max) if preco_max is not None else None,
        }
    except ValueError as exc:
        raise AppError("Filtros de preço inválidos", 400) from exc
