from app_factory import create_app
from config import Config
from database import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
