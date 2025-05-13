from app import db

class Veicolo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    targa = db.Column(db.String(20), nullable=False)
    marca = db.Column(db.String(50))
    modello = db.Column(db.String(50))
    anno = db.Column(db.Integer)
    km = db.Column(db.Integer)
    scadenze = db.relationship('Scadenza', backref='veicolo', lazy=True)
    logs = db.relationship('KmLog', backref='veicolo', lazy=True)


class Scadenza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicolo.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)

    veicolo = db.relationship('Veicolo', backref=db.backref('scadenze', lazy=True))

class Scadenza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicolo.id'), nullable=False)
    tipo = db.Column(db.String(50))
    data = db.Column(db.Date)


class KmLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicolo.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    km = db.Column(db.Integer, nullable=False)
