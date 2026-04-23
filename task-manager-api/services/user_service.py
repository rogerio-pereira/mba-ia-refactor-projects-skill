import re

from config import Config
from database import db
from models.task import Task
from models.user import User
from services.auth_service import AuthService


class UserService:
    def __init__(self):
        self.auth_service = AuthService(Config.SECRET_KEY)

    def get_users(self):
        result = []
        for user in User.query.all():
            result.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
                'active': user.active,
                'created_at': str(user.created_at),
                'task_count': len(user.tasks),
            })
        return result

    def get_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}, 404

        data = user.to_dict()
        data['tasks'] = [task.to_dict() for task in Task.query.filter_by(user_id=user_id).all()]
        return data, 200

    def create_user(self, data):
        if not data:
            return {'error': 'Dados inválidos'}, 400

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not name:
            return {'error': 'Nome é obrigatório'}, 400
        if not email:
            return {'error': 'Email é obrigatório'}, 400
        if not password:
            return {'error': 'Senha é obrigatória'}, 400
        if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
            return {'error': 'Email inválido'}, 400
        if len(password) < 4:
            return {'error': 'Senha deve ter no mínimo 4 caracteres'}, 400
        if role not in ['user', 'admin', 'manager']:
            return {'error': 'Role inválido'}, 400
        if User.query.filter_by(email=email).first():
            return {'error': 'Email já cadastrado'}, 409

        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.role = role

        try:
            db.session.add(user)
            db.session.commit()
            return user.to_dict(), 201
        except Exception:
            db.session.rollback()
            return {'error': 'Erro ao criar usuário'}, 500

    def update_user(self, user_id, data):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}, 404
        if not data:
            return {'error': 'Dados inválidos'}, 400

        if 'name' in data:
            user.name = data['name']

        if 'email' in data:
            if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', data['email']):
                return {'error': 'Email inválido'}, 400
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return {'error': 'Email já cadastrado'}, 409
            user.email = data['email']

        if 'password' in data:
            if len(data['password']) < 4:
                return {'error': 'Senha muito curta'}, 400
            user.set_password(data['password'])

        if 'role' in data:
            if data['role'] not in ['user', 'admin', 'manager']:
                return {'error': 'Role inválido'}, 400
            user.role = data['role']

        if 'active' in data:
            user.active = data['active']

        try:
            db.session.commit()
            return user.to_dict(), 200
        except Exception:
            db.session.rollback()
            return {'error': 'Erro ao atualizar'}, 500

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}, 404

        for task in Task.query.filter_by(user_id=user_id).all():
            db.session.delete(task)

        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'Usuário deletado com sucesso'}, 200
        except Exception:
            db.session.rollback()
            return {'error': 'Erro ao deletar'}, 500

    def get_user_tasks(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}, 404

        result = []
        for task in Task.query.filter_by(user_id=user_id).all():
            result.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'created_at': str(task.created_at),
                'due_date': str(task.due_date) if task.due_date else None,
                'overdue': task.is_overdue(),
            })
        return result, 200

    def login(self, data):
        if not data:
            return {'error': 'Dados inválidos'}, 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'error': 'Email e senha são obrigatórios'}, 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return {'error': 'Credenciais inválidas'}, 401
        if not user.check_password(password):
            return {'error': 'Credenciais inválidas'}, 401
        if not user.active:
            return {'error': 'Usuário inativo'}, 403

        if self.auth_service.needs_rehash(user.password):
            user.password = self.auth_service.hash_password(password)
            db.session.commit()

        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': self.auth_service.generate_token(user),
        }, 200
