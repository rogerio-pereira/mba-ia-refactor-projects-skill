from database import db
from models.category import Category
from models.task import Task


class CategoryService:
    def get_categories(self):
        result = []
        for category in Category.query.all():
            category_data = category.to_dict()
            category_data['task_count'] = Task.query.filter_by(category_id=category.id).count()
            result.append(category_data)
        return result

    def create_category(self, data):
        if not data:
            return {'error': 'Dados inválidos'}, 400

        name = data.get('name')
        if not name:
            return {'error': 'Nome é obrigatório'}, 400

        category = Category()
        category.name = name
        category.description = data.get('description', '')
        category.color = data.get('color', '#000000')

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

        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        if 'color' in data:
            category.color = data['color']

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
