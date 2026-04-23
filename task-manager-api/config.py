import os

from dotenv import load_dotenv


load_dotenv()


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    DEBUG = _as_bool(os.getenv('FLASK_DEBUG'), default=False)
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    PORT = int(os.getenv('FLASK_PORT', '5000'))
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.example.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', 'taskmanager@example.com')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'change-me')
