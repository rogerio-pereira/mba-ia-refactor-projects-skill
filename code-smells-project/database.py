import sqlite3
from flask import current_app, g
from werkzeug.security import generate_password_hash


def _connect():
    db_path = current_app.config["DATABASE_PATH"]
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _is_password_hash(value):
    return value.startswith("scrypt:") or value.startswith("pbkdf2:")


def _migrate_legacy_passwords(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("SELECT id, senha FROM usuarios")
    usuarios = cursor.fetchall()
    atualizou = False

    for usuario in usuarios:
        if _is_password_hash(usuario["senha"]):
            continue
        cursor.execute(
            "UPDATE usuarios SET senha = ? WHERE id = ?",
            (generate_password_hash(usuario["senha"]), usuario["id"]),
        )
        atualizou = True

    if atualizou:
        db_connection.commit()


def _create_schema(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL DEFAULT '',
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'cliente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pendente',
            total REAL NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)
    db_connection.commit()


def _has_unique_email_constraint(db_connection):
    cursor = db_connection.execute("PRAGMA index_list(usuarios)")
    for row in cursor.fetchall():
        if row["unique"] != 1:
            continue
        columns = db_connection.execute(f"PRAGMA index_info({row['name']})").fetchall()
        if [column["name"] for column in columns] == ["email"]:
            return True
    return False


def _needs_schema_migration(db_connection):
    usuarios = {
        row["name"]: row
        for row in db_connection.execute("PRAGMA table_info(usuarios)").fetchall()
    }
    pedidos_foreign_keys = db_connection.execute("PRAGMA foreign_key_list(pedidos)").fetchall()
    itens_foreign_keys = db_connection.execute("PRAGMA foreign_key_list(itens_pedido)").fetchall()
    email_row = usuarios.get("email")

    return (
        email_row is None
        or email_row["notnull"] != 1
        or not _has_unique_email_constraint(db_connection)
        or len(pedidos_foreign_keys) == 0
        or len(itens_foreign_keys) < 2
    )


def _migrate_schema(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("ALTER TABLE produtos RENAME TO produtos_legacy")
    cursor.execute("ALTER TABLE usuarios RENAME TO usuarios_legacy")
    cursor.execute("ALTER TABLE pedidos RENAME TO pedidos_legacy")
    cursor.execute("ALTER TABLE itens_pedido RENAME TO itens_pedido_legacy")

    _create_schema(db_connection)

    cursor.execute(
        """
        INSERT INTO produtos (id, nome, descricao, preco, estoque, categoria, ativo, criado_em)
        SELECT id, COALESCE(nome, ''), COALESCE(descricao, ''), COALESCE(preco, 0), COALESCE(estoque, 0),
               COALESCE(categoria, 'geral'), COALESCE(ativo, 1), criado_em
        FROM produtos_legacy
        """
    )
    cursor.execute(
        """
        INSERT INTO usuarios (id, nome, email, senha, tipo, criado_em)
        SELECT u.id, COALESCE(u.nome, ''), u.email, COALESCE(u.senha, ''), COALESCE(u.tipo, 'cliente'), u.criado_em
        FROM usuarios_legacy u
        WHERE u.email IS NOT NULL
          AND TRIM(u.email) <> ''
          AND u.id = (
              SELECT MIN(id)
              FROM usuarios_legacy dedupe
              WHERE dedupe.email = u.email
          )
        """
    )
    cursor.execute(
        """
        INSERT INTO pedidos (id, usuario_id, status, total, criado_em)
        SELECT p.id, p.usuario_id, COALESCE(p.status, 'pendente'), COALESCE(p.total, 0), p.criado_em
        FROM pedidos_legacy p
        INNER JOIN usuarios u ON u.id = p.usuario_id
        """
    )
    cursor.execute(
        """
        INSERT INTO itens_pedido (id, pedido_id, produto_id, quantidade, preco_unitario)
        SELECT i.id, i.pedido_id, i.produto_id, COALESCE(i.quantidade, 0), COALESCE(i.preco_unitario, 0)
        FROM itens_pedido_legacy i
        INNER JOIN pedidos p ON p.id = i.pedido_id
        INNER JOIN produtos pr ON pr.id = i.produto_id
        """
    )

    cursor.execute("DROP TABLE itens_pedido_legacy")
    cursor.execute("DROP TABLE pedidos_legacy")
    cursor.execute("DROP TABLE usuarios_legacy")
    cursor.execute("DROP TABLE produtos_legacy")
    db_connection.commit()
    cursor.execute("PRAGMA foreign_keys = ON")


def _seed_data(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] != 0:
        return

    produtos = [
        ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
        ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
        ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
        ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
        ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
        ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
        ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
        ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
        ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
        ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
    ]
    cursor.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        produtos
    )

    usuarios = [
        ("Admin", "admin@loja.com", generate_password_hash("admin123"), "admin"),
        ("João Silva", "joao@email.com", generate_password_hash("123456"), "cliente"),
        ("Maria Santos", "maria@email.com", generate_password_hash("senha123"), "cliente"),
    ]
    cursor.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        usuarios
    )
    db_connection.commit()


def init_db():
    db_connection = _connect()
    try:
        _create_schema(db_connection)
        if _needs_schema_migration(db_connection):
            _migrate_schema(db_connection)
        _seed_data(db_connection)
        _migrate_legacy_passwords(db_connection)
    finally:
        db_connection.close()

def get_db():
    if "db_connection" not in g:
        g.db_connection = _connect()

    return g.db_connection


def close_db(_error=None):
    db_connection = g.pop("db_connection", None)
    if db_connection is not None:
        db_connection.close()
