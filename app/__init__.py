from flask import Flask
from app.extensions import db, migrate
from app.routes.dashboard import dashboard_bp
from app.routes.veicoli import veicoli_bp
from app.routes.fornitori import fornitori_bp  
from app.routes.manutenzioni import manutenzioni_bp
from app.routes.scadenze import scadenze_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Inizializza estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    
    # IMPORTANTE: Importa i modelli DOPO aver inizializzato db
    from app import models
    
    # Registra blueprint
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(veicoli_bp, url_prefix='/veicoli')
    app.register_blueprint(fornitori_bp, url_prefix='/fornitori')
    app.register_blueprint(manutenzioni_bp, url_prefix='/manutenzioni')
    app.register_blueprint(scadenze_bp, url_prefix='/scadenze')
    
    # Crea tabelle
    with app.app_context():
        db.create_all()
    
    return app
