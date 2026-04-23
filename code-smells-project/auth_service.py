import user_repository
from errors import AppError
from werkzeug.security import check_password_hash, generate_password_hash


def _is_password_hash(value):
    return value.startswith("scrypt:") or value.startswith("pbkdf2:")


def criar_usuario(nome, email, senha, tipo="cliente"):
    if user_repository.get_usuario_por_email(email) is not None:
        raise AppError("Email já cadastrado", 400)

    senha_hash = generate_password_hash(senha)
    return user_repository.criar_usuario(nome, email, senha_hash, tipo)


def login_usuario(email, senha):
    row = user_repository.get_usuario_por_email(email)
    if row is None:
        return None

    senha_salva = row["senha"]
    if _is_password_hash(senha_salva):
        autenticado = check_password_hash(senha_salva, senha)
    else:
        autenticado = senha_salva == senha
        if autenticado:
            user_repository.atualizar_senha(row["id"], generate_password_hash(senha))

    if autenticado:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"]
        }
    return None
