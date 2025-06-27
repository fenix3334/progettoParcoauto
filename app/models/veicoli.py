from app.extensions import db
from datetime import datetime

class Veicolo(db.Model):
    __tablename__ = 'veicoli'
    
    id = db.Column(db.Integer, primary_key=True)
    targa = db.Column(db.String(10), unique=True, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modello = db.Column(db.String(50), nullable=False)
    anno_immatricolazione = db.Column(db.Integer, nullable=False)
    data_immatricolazione = db.Column(db.Date, nullable=False)
    km_attuali = db.Column(db.Integer, default=0)
    carburante = db.Column(db.String(20), nullable=False)
    cilindrata = db.Column(db.Integer)
    colore = db.Column(db.String(30))
    stato = db.Column(db.String(20), default='Attivo')
    note = db.Column(db.Text)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    manutenzioni = db.relationship('Manutenzione', backref='veicolo', lazy=True)
    scadenze = db.relationship('Scadenza', backref='veicolo', lazy=True)
    
    def __repr__(self):
        return f'<Veicolo {self.targa} - {self.marca} {self.modello}>'
