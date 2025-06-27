from app.extensions import db
from datetime import datetime

class Scadenza(db.Model):
    __tablename__ = 'scadenze'
    
    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    tipo_scadenza = db.Column(db.String(50), nullable=False)  # Revisione, Assicurazione, Bollo, ecc.
    data_scadenza = db.Column(db.Date, nullable=False)
    costo = db.Column(db.Numeric(10, 2))
    stato = db.Column(db.String(20), default='Attiva')  # Attiva, Scaduta, Rinnovata
    note = db.Column(db.Text)
    notifica_giorni = db.Column(db.Integer, default=30)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def giorni_alla_scadenza(self):
        from datetime import date
        return (self.data_scadenza - date.today()).days
    
    @property
    def is_urgente(self):
        return self.giorni_alla_scadenza <= self.notifica_giorni
    
    def __repr__(self):
        return f'<Scadenza {self.tipo_scadenza} - {self.data_scadenza}>'
