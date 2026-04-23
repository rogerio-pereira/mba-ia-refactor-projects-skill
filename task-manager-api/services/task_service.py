from datetime import datetime

from sqlalchemy.orm import joinedload

from database import db
from errors import ApiError, NotFoundError, ValidationError
from models.category import Category
from models.task import Task
from models.user import User
from services.validation_service import ValidationService


class TaskService:
    def __init__(self):
        self.validation_service = ValidationService()

    def _serialize_task(self, task):
        task_data = {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'user_id': task.user_id,
            'category_id': task.category_id,
            'created_at': str(task.created_at),
            'updated_at': str(task.updated_at),
            'due_date': str(task.due_date) if task.due_date else None,
            'tags': task.tags.split(',') if task.tags else [],
            'overdue': task.is_overdue(),
        }

        task_data['user_name'] = task.user.name if task.user else None
        task_data['category_name'] = task.category.name if task.category else None

        return task_data

    def get_tasks(self):
        tasks = Task.query.options(
            joinedload(Task.user),
            joinedload(Task.category),
        ).all()
        return [self._serialize_task(task) for task in tasks]

    def get_task(self, task_id):
        task = db.session.get(Task, task_id)
        if not task:
            raise NotFoundError('Task não encontrada')

        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        return data

    def create_task(self, data):
        normalized, error = self.validation_service.validate_task_payload(data)
        if error:
            raise ValidationError(error)

        if normalized['user_id']:
            user = db.session.get(User, normalized['user_id'])
            if not user:
                raise NotFoundError('Usuário não encontrado')

        if normalized['category_id']:
            category = db.session.get(Category, normalized['category_id'])
            if not category:
                raise NotFoundError('Categoria não encontrada')

        task = Task()
        task.title = normalized['title']
        task.description = normalized['description']
        task.status = normalized['status']
        task.priority = normalized['priority']
        task.user_id = normalized['user_id']
        task.category_id = normalized['category_id']
        task.due_date = normalized['due_date']
        task.tags = normalized['tags']

        try:
            db.session.add(task)
            db.session.commit()
            return task.to_dict()
        except Exception as exc:
            db.session.rollback()
            raise ApiError('Erro ao criar task') from exc

    def update_task(self, task_id, data):
        task = db.session.get(Task, task_id)
        if not task:
            raise NotFoundError('Task não encontrada')

        normalized, error = self.validation_service.validate_task_payload(data, partial=True)
        if error:
            raise ValidationError(error)

        if 'user_id' in normalized:
            if normalized['user_id']:
                user = db.session.get(User, normalized['user_id'])
                if not user:
                    raise NotFoundError('Usuário não encontrado')
            task.user_id = normalized['user_id']

        if 'category_id' in normalized:
            if normalized['category_id']:
                category = db.session.get(Category, normalized['category_id'])
                if not category:
                    raise NotFoundError('Categoria não encontrada')
            task.category_id = normalized['category_id']

        for field in ['title', 'description', 'status', 'priority', 'due_date', 'tags']:
            if field in normalized:
                setattr(task, field, normalized[field])

        task.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            return task.to_dict()
        except Exception as exc:
            db.session.rollback()
            raise ApiError('Erro ao atualizar') from exc

    def delete_task(self, task_id):
        task = db.session.get(Task, task_id)
        if not task:
            raise NotFoundError('Task não encontrada')

        try:
            db.session.delete(task)
            db.session.commit()
            return {'message': 'Task deletada com sucesso'}
        except Exception as exc:
            db.session.rollback()
            raise ApiError('Erro ao deletar') from exc

    def search_tasks(self, filters):
        tasks = Task.query
        query = filters.get('q', '')
        status = filters.get('status', '')
        priority = filters.get('priority', '')
        user_id = filters.get('user_id', '')

        if query:
            tasks = tasks.filter(
                db.or_(
                    Task.title.like(f'%{query}%'),
                    Task.description.like(f'%{query}%')
                )
            )

        if status:
            tasks = tasks.filter(Task.status == status)
        if priority:
            tasks = tasks.filter(Task.priority == int(priority))
        if user_id:
            tasks = tasks.filter(Task.user_id == int(user_id))

        return [task.to_dict() for task in tasks.all()]

    def task_stats(self):
        total = Task.query.count()
        done = Task.query.filter_by(status='done').count()

        return {
            'total': total,
            'pending': Task.query.filter_by(status='pending').count(),
            'in_progress': Task.query.filter_by(status='in_progress').count(),
            'done': done,
            'cancelled': Task.query.filter_by(status='cancelled').count(),
            'overdue': sum(1 for task in Task.query.all() if task.is_overdue()),
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        }
