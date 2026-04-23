import hashlib

from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash


class AuthService:
    def __init__(self, secret_key=None):
        self.serializer = URLSafeTimedSerializer(secret_key) if secret_key else None

    def hash_password(self, password):
        return generate_password_hash(password)

    def check_password(self, stored_password, password):
        if not stored_password:
            return False

        if stored_password.startswith('pbkdf2:') or stored_password.startswith('scrypt:'):
            return check_password_hash(stored_password, password)

        legacy_hash = hashlib.md5(password.encode()).hexdigest()
        return stored_password == legacy_hash

    def needs_rehash(self, stored_password):
        if not stored_password:
            return True
        return not (
            stored_password.startswith('pbkdf2:')
            or stored_password.startswith('scrypt:')
        )

    def generate_token(self, user):
        if not self.serializer:
            raise ValueError('Token serializer is not configured')
        return self.serializer.dumps({
            'sub': user.id,
            'email': user.email,
            'role': user.role,
        })
