from database import get_db
import order_repository
import product_repository


def criar_pedido(usuario_id, itens):
    db = get_db()
    produtos = product_repository.get_produtos_por_ids([item["produto_id"] for item in itens])
    total = 0

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
        order_repository.criar_item_pedido(
            pedido_id,
            item["produto_id"],
            item["quantidade"],
            produto["preco"],
        )
        product_repository.atualizar_estoque(item["produto_id"], item["quantidade"])

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def listar_pedidos(rows):
    pedidos = []
    pedido_ids = [row["id"] for row in rows]
    itens = order_repository.get_itens_por_pedido_ids(pedido_ids)
    itens_por_pedido = {}
    produto_ids = []

    for item in itens:
        itens_por_pedido.setdefault(item["pedido_id"], []).append(item)
        produto_ids.append(item["produto_id"])

    produtos = product_repository.get_produtos_por_ids(produto_ids)

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
    return order_repository.atualizar_status_pedido(pedido_id, novo_status)
