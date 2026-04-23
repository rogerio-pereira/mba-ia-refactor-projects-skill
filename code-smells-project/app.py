from flask import Flask, jsonify
from flask_cors import CORS
import controllers
from database import close_db, init_db
from config import Config
from errors import AppError

def register_routes(app):
    app.add_url_rule("/produtos", "listar_produtos", controllers.listar_produtos, methods=["GET"])
    app.add_url_rule("/produtos/busca", "buscar_produtos", controllers.buscar_produtos, methods=["GET"])
    app.add_url_rule("/produtos/<int:id>", "buscar_produto", controllers.buscar_produto, methods=["GET"])
    app.add_url_rule("/produtos", "criar_produto", controllers.criar_produto, methods=["POST"])
    app.add_url_rule("/produtos/<int:id>", "atualizar_produto", controllers.atualizar_produto, methods=["PUT"])
    app.add_url_rule("/produtos/<int:id>", "deletar_produto", controllers.deletar_produto, methods=["DELETE"])

    app.add_url_rule("/usuarios", "listar_usuarios", controllers.listar_usuarios, methods=["GET"])
    app.add_url_rule("/usuarios/<int:id>", "buscar_usuario", controllers.buscar_usuario, methods=["GET"])
    app.add_url_rule("/usuarios", "criar_usuario", controllers.criar_usuario, methods=["POST"])
    app.add_url_rule("/login", "login", controllers.login, methods=["POST"])

    app.add_url_rule("/pedidos", "criar_pedido", controllers.criar_pedido, methods=["POST"])
    app.add_url_rule("/pedidos", "listar_todos_pedidos", controllers.listar_todos_pedidos, methods=["GET"])
    app.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", controllers.listar_pedidos_usuario, methods=["GET"])
    app.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", controllers.atualizar_status_pedido, methods=["PUT"])

    app.add_url_rule("/relatorios/vendas", "relatorio_vendas", controllers.relatorio_vendas, methods=["GET"])
    app.add_url_rule("/health", "health_check", controllers.health_check, methods=["GET"])


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    if app.config["APP_ENV"] != "development" and Config.uses_placeholder_secret():
        raise RuntimeError("SECRET_KEY must be configured with a non-placeholder value outside development")

    if app.config["CORS_ORIGINS"]:
        CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
    register_routes(app)

    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({"erro": error.message, "sucesso": False}), error.status_code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled error", exc_info=error)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500

    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health"
            }
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.logger.info("Servidor iniciado em http://%s:%s", app.config["HOST"], app.config["PORT"])

    app.run(host=app.config["HOST"], port=app.config["PORT"], debug=app.config["DEBUG"])
