from datetime import datetime

from database import db
from models.category import Category
from models.task import Task
from models.user import User


class TaskService:
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

        if task.user_id:
            user = User.query.get(task.user_id)
            task_data['user_name'] = user.name if user else None
        else:
            task_data['user_name'] = None

        if task.category_id:
            category = Category.query.get(task.category_id)
            task_data['category_name'] = category.name if category else None
        else:
            task_data['category_name'] = None

        return task_data

    def get_tasks(self):
        return [self._serialize_task(task) for task in Task.query.all()]

    def get_task(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return None

        data = task.to_dict()
        data['overdue'] = task.is_overdue()
        return data

    def create_task(self, data):
        if not data:
            return {'error': 'Dados inválidos'}, 400

        title = data.get('title')
        if not title:
            return {'error': 'Título é obrigatório'}, 400
        if len(title) < 3:
            return {'error': 'Título muito curto'}, 400
        if len(title) > 200:
            return {'error': 'Título muito longo'}, 400

        description = data.get('description', '')
        status = data.get('status', 'pending')
        priority = data.get('priority', 3)
        user_id = data.get('user_id')
        category_id = data.get('category_id')
        due_date = data.get('due_date')
        tags = data.get('tags')

        if status not in ['pending', 'in_progress', 'done', 'cancelled']:
            return {'error': 'Status inválido'}, 400
        if priority < 1 or priority > 5:
            return {'error': 'Prioridade deve ser entre 1 e 5'}, 400

        if user_id:
            user = User.query.get(user_id)
            if not user:
                return {'error': 'Usuário não encontrado'}, 404

        if category_id:
            category = Category.query.get(category_id)
            if not category:
                return {'error': 'Categoria não encontrada'}, 404

        task = Task()
        task.title = title
        task.description = description
        task.status = status
        task.priority = priority
        task.user_id = user_id
        task.category_id = category_id

        if due_date:
            try:
                task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                return {'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 400

        if tags:
            task.tags = ','.join(tags) if isinstance(tags, list) else tags

        try:
            db.session.add(task)
            db.session.commit()
            return task.to_dict(), 201
        except Exception:
            db.session.rollback()
            return {'error': 'Erro ao criar task'}, 500

    def update_task(self, task_id, data):
        task = Task.query.get(task_id)
        if not task:
            return {'error': 'Task não encontrada'}, 404
        if not data:
            return {'error': 'Dados inválidos'}, 400

        if 'title' in data:
            if len(data['title']) < 3:
                return {'error': 'Título muito curto'}, 400
            if len(data['title']) > 200:
                return {'error': 'Título muito longo'}, 400
            task.title = data['title']

        if 'description' in data:
            task.description = data['description']

        if 'status' in data:
            if data['status'] not in ['pending', 'in_progress', 'done', 'cancelled']:
                return {'error': 'Status inválido'}, 400
            task.status = data['status']

        if 'priority' in data:
            if data['priority'] < 1 or data['priority'] > 5:
                return {'error': 'Prioridade deve ser entre 1 e 5'}, 400
            task.priority = data['priority']

        if 'user_id' in data:
            if data['user_id']:
                user = User.query.get(data['user_id'])
                if not user:
                    return {'error': 'Usuário não encontrado'}, 404
            task.user_id = data['user_id']

        if 'category_id' in data:
            if data['category_id']:
                category = Category.query.get(data['category_id'])
                if not category:
                    return {'error': 'Categoria não encontrada'}, 404
            task.category_id = data['category_id']

        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
                except ValueError:
                    return {'error': 'Formato de data inválido'}, 400
            else:
                task.due_date = None

        if 'tags' in data:
            task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

        task.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            return task.to_dict(), 200
        except Exception:
            db.session.rollback()
            return {'error': 'Erro ao atualizar'}, 500

    def delete_task(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {'error': 'Task não encontrada'}, 404

        try:
            db.session.delete(task)
            db.session.commit()
            return {'message': 'Task deletada com sucesso'}, 200
        except Exception:
            db.session.rollback()
            return {'error': 'Erro ao deletar'}, 500

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
