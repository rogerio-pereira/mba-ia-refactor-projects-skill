from database import get_db
from errors import AppError
import notification_service
import order_repository
import product_repository


def criar_pedido(usuario_id, itens):
    db = get_db()
    produtos = product_repository.get_produtos_por_ids([item["produto_id"] for item in itens])
    total = 0

    try:
        for item in itens:
            produto = produtos.get(item["produto_id"])
            if produto is None:
                return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": "Estoque insuficiente para " + produto["nome"]}
            total += produto["preco"] * item["quantidade"]

        pedido_id = order_repository.criar_pedido(usuario_id, "pendente", total)
        for item in itens:
            produto = produtos[item["produto_id"]]
            if not product_repository.reservar_estoque(item["produto_id"], item["quantidade"]):
                db.rollback()
                return {"erro": "Estoque insuficiente para " + produto["nome"]}
            order_repository.criar_item_pedido(
                pedido_id,
                item["produto_id"],
                item["quantidade"],
                produto["preco"],
            )

        db.commit()
        notification_service.notificar_pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}
    except Exception:
        db.rollback()
        raise


def listar_pedidos(rows):
    pedidos = []
    pedido_ids = [row["id"] for row in rows]
    itens = order_repository.get_itens_por_pedido_ids(pedido_ids)
    itens_por_pedido = {}
    produto_ids = set()

    for item in itens:
        itens_por_pedido.setdefault(item["pedido_id"], []).append(item)
        produto_ids.add(item["produto_id"])

    produtos = product_repository.get_produtos_por_ids(list(produto_ids))

    for row in rows:
        pedido = {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": []
        }
        for item in itens_por_pedido.get(row["id"], []):
            produto = produtos.get(item["produto_id"])
            pedido["itens"].append({
                "produto_id": item["produto_id"],
                "produto_nome": produto["nome"] if produto else "Desconhecido",
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"]
            })
        pedidos.append(pedido)

    return pedidos


def get_pedidos_usuario(usuario_id):
    return listar_pedidos(order_repository.get_pedidos_usuario(usuario_id))


def get_todos_pedidos():
    return listar_pedidos(order_repository.get_todos_pedidos())


def atualizar_status_pedido(pedido_id, novo_status):
    resultado = order_repository.atualizar_status_pedido(pedido_id, novo_status)
    if not resultado:
        raise AppError("Pedido não encontrado", 404)
    notification_service.notificar_status_pedido(pedido_id, novo_status)
    return resultado
