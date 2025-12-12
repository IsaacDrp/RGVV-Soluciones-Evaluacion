from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializador de extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Registro de blueprints (entidades)
    from app.controllers.main_controller import bp as main_bp
    from app.controllers.gastos_controller import bp as gastos_bp
    from app.controllers.pagos_controller import bp as pagos_bp
    from app.controllers.cuentas_controller import bp as cuentas_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(gastos_bp, url_prefix='/gastos')
    app.register_blueprint(pagos_bp, url_prefix='/pagos')
    app.register_blueprint(cuentas_bp, url_prefix='/cuentas')
    
    # Creacion de tablas en caso de no existir
    with app.app_context():
        db.create_all()
    
    return app