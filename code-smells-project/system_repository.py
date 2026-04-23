from database import get_db


def get_health_counts():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    produtos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    usuarios = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    pedidos = cursor.fetchone()[0]
    return {
        "produtos": produtos,
        "usuarios": usuarios,
        "pedidos": pedidos,
    }
