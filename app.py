from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)

    # importa modelli e crea tabelle
    import models
    with app.app_context():
        db.create_all()

    # registra blueprints
    from blueprints.vehicoli import vehicoli_bp
    from blueprints.scadenze import scadenze_bp
    from blueprints.dashboard import dashboard_bp
    from blueprints.report_km import report_bp
    app.register_blueprint(vehicoli_bp)
    app.register_blueprint(scadenze_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(report_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
