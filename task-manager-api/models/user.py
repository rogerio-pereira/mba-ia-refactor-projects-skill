from database import db
from datetime import datetime

from services.auth_service import AuthService

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, pwd):
        auth_service = AuthService()
        self.password = auth_service.hash_password(pwd)

    def check_password(self, pwd):
        auth_service = AuthService()
        return auth_service.check_password(self.password, pwd)

    def is_admin(self):
        if self.role == 'admin':
            return True
        else:
            return False
