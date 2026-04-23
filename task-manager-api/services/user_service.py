from config import Config
from database import db
from errors import ApiError, ConflictError, NotFoundError, ValidationError
from models.task import Task
from models.user import User
from services.auth_service import AuthService
from services.validation_service import ValidationService


class UserService:
    def __init__(self):
        self.auth_service = AuthService(Config.SECRET_KEY)
        self.validation_service = ValidationService()

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
            raise NotFoundError('Usuário não encontrado')

        data = user.to_dict()
        data['tasks'] = [task.to_dict() for task in Task.query.filter_by(user_id=user_id).all()]
        return data

    def create_user(self, data):
        normalized, error = self.validation_service.validate_user_payload(data)
        if error:
            raise ValidationError(error)

        if User.query.filter_by(email=normalized['email']).first():
            raise ConflictError('Email já cadastrado')

        user = User()
        user.name = normalized['name']
        user.email = normalized['email']
        user.set_password(normalized['password'])
        user.role = normalized['role']

        try:
            db.session.add(user)
            db.session.commit()
            return user.to_dict()
        except Exception as exc:
            db.session.rollback()
            raise ApiError('Erro ao criar usuário') from exc

    def update_user(self, user_id, data):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')

        normalized, error = self.validation_service.validate_user_payload(data, partial=True)
        if error:
            raise ValidationError(error)

        if 'name' in normalized:
            user.name = normalized['name']

        if 'email' in normalized:
            existing = User.query.filter_by(email=normalized['email']).first()
            if existing and existing.id != user_id:
                raise ConflictError('Email já cadastrado')
            user.email = normalized['email']

        if 'password' in normalized:
            user.set_password(normalized['password'])

        if 'role' in normalized:
            user.role = normalized['role']

        if 'active' in normalized:
            user.active = normalized['active']

        try:
            db.session.commit()
            return user.to_dict()
        except Exception as exc:
            db.session.rollback()
            raise ApiError('Erro ao atualizar') from exc

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')

        for task in Task.query.filter_by(user_id=user_id).all():
            db.session.delete(task)

        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'Usuário deletado com sucesso'}
        except Exception as exc:
            db.session.rollback()
            raise ApiError('Erro ao deletar') from exc

    def get_user_tasks(self, user_id):
        user = User.query.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')

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
        return result

    def login(self, data):
        if not data:
            raise ValidationError('Dados inválidos')

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise ValidationError('Email e senha são obrigatórios')

        user = User.query.filter_by(email=email).first()
        if not user:
            raise ValidationError('Credenciais inválidas', status_code=401)
        if not user.check_password(password):
            raise ValidationError('Credenciais inválidas', status_code=401)
        if not user.active:
            raise ValidationError('Usuário inativo', status_code=403)

        if self.auth_service.needs_rehash(user.password):
            user.password = self.auth_service.hash_password(password)
            db.session.commit()

        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': self.auth_service.generate_token(user),
        }
