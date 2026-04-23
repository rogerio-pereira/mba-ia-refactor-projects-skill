from datetime import datetime, timedelta

from models.category import Category
from models.task import Task
from models.user import User


class ReportService:
    def summary_report(self):
        total_tasks = Task.query.count()
        total_users = User.query.count()
        total_categories = Category.query.count()

        overdue_list = []
        overdue_count = 0
        for task in Task.query.all():
            if task.is_overdue():
                overdue_count += 1
                overdue_list.append({
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (datetime.utcnow() - task.due_date).days,
                })

        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
        recent_done = Task.query.filter(
            Task.status == 'done',
            Task.updated_at >= seven_days_ago
        ).count()

        user_stats = []
        for user in User.query.all():
            user_tasks = Task.query.filter_by(user_id=user.id).all()
            total = len(user_tasks)
            completed = sum(1 for task in user_tasks if task.status == 'done')
            user_stats.append({
                'user_id': user.id,
                'user_name': user.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
            })

        return {
            'generated_at': str(datetime.utcnow()),
            'overview': {
                'total_tasks': total_tasks,
                'total_users': total_users,
                'total_categories': total_categories,
            },
            'tasks_by_status': {
                'pending': Task.query.filter_by(status='pending').count(),
                'in_progress': Task.query.filter_by(status='in_progress').count(),
                'done': Task.query.filter_by(status='done').count(),
                'cancelled': Task.query.filter_by(status='cancelled').count(),
            },
            'tasks_by_priority': {
                'critical': Task.query.filter_by(priority=1).count(),
                'high': Task.query.filter_by(priority=2).count(),
                'medium': Task.query.filter_by(priority=3).count(),
                'low': Task.query.filter_by(priority=4).count(),
                'minimal': Task.query.filter_by(priority=5).count(),
            },
            'overdue': {
                'count': overdue_count,
                'tasks': overdue_list,
            },
            'recent_activity': {
                'tasks_created_last_7_days': recent_tasks,
                'tasks_completed_last_7_days': recent_done,
            },
            'user_productivity': user_stats,
        }

    def user_report(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Usuário não encontrado'}, 404

        tasks = Task.query.filter_by(user_id=user_id).all()
        done = 0
        pending = 0
        in_progress = 0
        cancelled = 0
        overdue = 0
        high_priority = 0

        for task in tasks:
            if task.status == 'done':
                done += 1
            elif task.status == 'pending':
                pending += 1
            elif task.status == 'in_progress':
                in_progress += 1
            elif task.status == 'cancelled':
                cancelled += 1

            if task.priority <= 2:
                high_priority += 1
            if task.is_overdue():
                overdue += 1

        total = len(tasks)
        return {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
            },
            'statistics': {
                'total_tasks': total,
                'done': done,
                'pending': pending,
                'in_progress': in_progress,
                'cancelled': cancelled,
                'overdue': overdue,
                'high_priority': high_priority,
                'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
            }
        }, 200
