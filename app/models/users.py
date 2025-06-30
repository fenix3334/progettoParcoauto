from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nucleo = db.Column(db.String(50), default='Via Capitel')
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_accesso = db.Column(db.DateTime)
    
    def check_password(self, password):
        return self.password_hash == password
    
    def set_password(self, password):
        self.password_hash = password

    def __repr__(self):
        return f'<User {self.username}>'