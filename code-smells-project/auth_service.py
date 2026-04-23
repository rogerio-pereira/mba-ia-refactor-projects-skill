import user_repository


def login_usuario(email, senha):
    row = user_repository.get_usuario_por_email_e_senha(email, senha)
    if row:
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"]
        }
    return None
