from sqlalchemy import func

from database import db
from models.category import Category
from models.task import Task
from services.validation_service import ValidationService


class CategoryService:
    def __init__(self):
        self.validation_service = ValidationService()

    def get_categories(self):
        task_counts = dict(
            db.session.query(Task.category_id, func.count(Task.id))
            .filter(Task.category_id.isnot(None))
            .group_by(Task.category_id)
            .all()
        )
        result = []
        for category in Category.query.all():
            category_data = category.to_dict()
            category_data['task_count'] = task_counts.get(category.id, 0)
            result.append(category_data)
        return result

    def create_category(self, data):
        normalized, error = self.validation_service.validate_category_payload(data)
        if error:
            return {'error': error}, 400

        category = Category()
        category.name = normalized['name']
        category.description = normalized['description']
        category.color = normalized['color']

        try:
            db.session.add(category)
            db.session.commit()
            return category.to_dict(), 201
        except Exception:
            db.session.rollback()
            return {'error': 'Erro ao criar categoria'}, 500

    def update_category(self, cat_id, data):
        category = Category.query.get(cat_id)
        if not category:
            return {'error': 'Categoria não encontrada'}, 404

        normalized, error = self.validation_service.validate_category_payload(data, partial=True)
        if error:
            return {'error': error}, 400

        for field in ['name', 'description', 'color']:
            if field in normalized:
                setattr(category, field, normalized[field])

        try:
            db.session.commit()
            return category.to_dict(), 200
        except Exception:
            db.session.rollback()
            return {'error': 'Erro ao atualizar'}, 500

    def delete_category(self, cat_id):
        category = Category.query.get(cat_id)
        if not category:
            return {'error': 'Categoria não encontrada'}, 404

        try:
            db.session.delete(category)
            db.session.commit()
            return {'message': 'Categoria deletada'}, 200
        except Exception:
            db.session.rollback()
            return {'error': 'Erro ao deletar'}, 500
