from app.extensions import db
from datetime import datetime

class Fornitore(db.Model):
    __tablename__ = 'fornitori'
    
    id = db.Column(db.Integer, primary_key=True)
    ragione_sociale = db.Column(db.String(100), nullable=False)
    partita_iva = db.Column(db.String(20), unique=True)
    codice_fiscale = db.Column(db.String(20))
    indirizzo = db.Column(db.String(200))
    citta = db.Column(db.String(50), nullable=False)
    cap = db.Column(db.String(10), nullable=False)
    provincia = db.Column(db.String(5))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    referente = db.Column(db.String(100))
    settore = db.Column(db.String(50))
    note = db.Column(db.Text)
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    manutenzioni = db.relationship('Manutenzione', backref='fornitore', lazy=True)
    
    def __repr__(self):
        return f'<Fornitore {self.ragione_sociale}>'
