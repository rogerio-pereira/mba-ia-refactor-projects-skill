from utils.helpers import (
    DEFAULT_COLOR,
    DEFAULT_PRIORITY,
    MIN_PASSWORD_LENGTH,
    VALID_ROLES,
    VALID_STATUSES,
    parse_date,
    sanitize_string,
    validate_email,
)


class ValidationService:
    def validate_task_payload(self, data, partial=False):
        if not data:
            return None, 'Dados inválidos'

        normalized = {}

        if not partial or 'title' in data:
            title = sanitize_string(data.get('title'))
            if not title:
                return None, 'Título é obrigatório' if not partial else 'Título não pode ser vazio'
            if len(title) < 3:
                return None, 'Título muito curto'
            if len(title) > 200:
                return None, 'Título muito longo'
            normalized['title'] = title

        if 'description' in data:
            normalized['description'] = data['description']
        elif not partial:
            normalized['description'] = data.get('description', '')

        if 'status' in data:
            if data['status'] not in VALID_STATUSES:
                return None, 'Status inválido'
            normalized['status'] = data['status']
        elif not partial:
            normalized['status'] = data.get('status', 'pending')

        if 'priority' in data:
            try:
                priority = int(data['priority'])
            except (TypeError, ValueError):
                return None, 'Prioridade inválida'
            if priority < 1 or priority > 5:
                return None, 'Prioridade deve ser entre 1 e 5'
            normalized['priority'] = priority
        elif not partial:
            normalized['priority'] = data.get('priority', DEFAULT_PRIORITY)

        if 'user_id' in data or not partial:
            normalized['user_id'] = data.get('user_id')

        if 'category_id' in data or not partial:
            normalized['category_id'] = data.get('category_id')

        if 'due_date' in data:
            if data['due_date']:
                parsed_date = parse_date(data['due_date'])
                if not parsed_date:
                    return None, 'Formato de data inválido. Use YYYY-MM-DD'
                normalized['due_date'] = parsed_date
            else:
                normalized['due_date'] = None
        elif not partial:
            normalized['due_date'] = None

        if 'tags' in data:
            tags = data['tags']
            normalized['tags'] = ','.join(tags) if isinstance(tags, list) else tags
        elif not partial:
            normalized['tags'] = data.get('tags')

        return normalized, None

    def validate_user_payload(self, data, partial=False):
        if not data:
            return None, 'Dados inválidos'

        normalized = {}

        if not partial or 'name' in data:
            name = sanitize_string(data.get('name'))
            if not name:
                return None, 'Nome é obrigatório' if not partial else 'Nome não pode ser vazio'
            normalized['name'] = name

        if not partial or 'email' in data:
            email = sanitize_string(data.get('email'))
            if not email:
                return None, 'Email é obrigatório' if not partial else 'Email inválido'
            if not validate_email(email):
                return None, 'Email inválido'
            normalized['email'] = email

        if not partial or 'password' in data:
            password = data.get('password')
            if not password:
                return None, 'Senha é obrigatória' if not partial else 'Senha muito curta'
            if len(password) < MIN_PASSWORD_LENGTH:
                if partial:
                    return None, 'Senha muito curta'
                return None, 'Senha deve ter no mínimo 4 caracteres'
            normalized['password'] = password

        if 'role' in data or not partial:
            role = data.get('role', 'user')
            if role not in VALID_ROLES:
                return None, 'Role inválido'
            normalized['role'] = role

        if 'active' in data:
            normalized['active'] = data['active']

        return normalized, None

    def validate_category_payload(self, data, partial=False):
        if not data:
            return None, 'Dados inválidos'

        normalized = {}

        if not partial or 'name' in data:
            name = sanitize_string(data.get('name'))
            if not name:
                return None, 'Nome é obrigatório'
            normalized['name'] = name

        if 'description' in data:
            normalized['description'] = data['description']
        elif not partial:
            normalized['description'] = data.get('description', '')

        if 'color' in data:
            normalized['color'] = data['color']
        elif not partial:
            normalized['color'] = data.get('color', DEFAULT_COLOR)

        return normalized, None
