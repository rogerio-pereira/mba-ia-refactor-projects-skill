from database import get_db


def criar_pedido(usuario_id, status, total):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, status, total),
    )
    return cursor.lastrowid


def criar_item_pedido(pedido_id, produto_id, quantidade, preco_unitario):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario),
    )


def get_pedidos_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
    return cursor.fetchall()


def get_todos_pedidos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos")
    return cursor.fetchall()


def get_itens_por_pedido_ids(pedido_ids):
    if not pedido_ids:
        return []

    placeholders = ", ".join(["?"] * len(pedido_ids))
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"SELECT * FROM itens_pedido WHERE pedido_id IN ({placeholders})",
        pedido_ids,
    )
    return cursor.fetchall()


def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    if cursor.rowcount != 1:
        return False

    db.commit()
    return True
