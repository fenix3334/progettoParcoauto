from app.extensions import db
from datetime import datetime

class Manutenzione(db.Model):
    __tablename__ = 'manutenzioni'
    
    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    fornitore_id = db.Column(db.Integer, db.ForeignKey('fornitori.id'))
    data_intervento = db.Column(db.Date, nullable=False)
    km_intervento = db.Column(db.Integer, nullable=False)
    tipo_intervento = db.Column(db.String(100), nullable=False)
    descrizione = db.Column(db.Text)
    costo = db.Column(db.Numeric(10, 2))
    numero_fattura = db.Column(db.String(50))
    data_fattura = db.Column(db.Date)
    garanzia_mesi = db.Column(db.Integer, default=0)
    prossima_scadenza_km = db.Column(db.Integer)
    note = db.Column(db.Text)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Manutenzione {self.tipo_intervento} - {self.data_intervento}>'
