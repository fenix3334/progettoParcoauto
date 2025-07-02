from app.extensions import db
from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Veicolo(db.Model):
    __tablename__ = 'veicoli'
    
    id = db.Column(db.Integer, primary_key=True)
    targa = db.Column(db.String(10), nullable=False, unique=True)
    marca = db.Column(db.String(50), nullable=False)
    modello = db.Column(db.String(50), nullable=False)
    anno_immatricolazione = db.Column(db.Integer, nullable=False)
    data_immatricolazione = db.Column(db.Date, nullable=False)
    km_attuali = db.Column(db.Integer, default=0)
    carburante = db.Column(db.String(20), nullable=False)
    carburante_personalizzato = db.Column(db.String(50))  # NUOVO CAMPO
    cilindrata = db.Column(db.Integer)
    colore = db.Column(db.String(30))
    stato = db.Column(db.String(20), default='Attivo')
    note = db.Column(db.Text)
    
    # NUOVI CAMPI PER CARTA CARBURANTE
    carta_carburante = db.Column(db.String(100))
    pin_carburante = db.Column(db.String(20))
    
    # NUOVO CAMPO PER SOCIETÀ NOLEGGIO
    societa_noleggio_id = db.Column(db.Integer, db.ForeignKey('fornitori.id'))
    
    # NUOVO CAMPO PER NUCLEO
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    manutenzioni = db.relationship('Manutenzione', backref='veicolo', lazy=True, 
                                 order_by='desc(Manutenzione.data_intervento)')
    scadenze = db.relationship('Scadenza', backref='veicolo', lazy=True,
                              order_by='desc(Scadenza.data_scadenza)')
    societa_noleggio = db.relationship('Fornitore', foreign_keys=[societa_noleggio_id])
    
    @property
    def nome_completo(self):
        return f"{self.targa} - {self.marca} {self.modello}"
    
    @property
    def carburante_display(self):
        return self.carburante_personalizzato if self.carburante_personalizzato else self.carburante

    def __repr__(self):
        return f'<Veicolo {self.targa}>'


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
    telefono_2 = db.Column(db.String(20))  # NUOVO CAMPO
    telefono_3 = db.Column(db.String(20))  # NUOVO CAMPO
    email = db.Column(db.String(100))
    email_2 = db.Column(db.String(100))    # NUOVO CAMPO
    email_3 = db.Column(db.String(100))    # NUOVO CAMPO
    referente = db.Column(db.String(100))
    settore = db.Column(db.String(50))
    settore_2 = db.Column(db.String(50))   # NUOVO CAMPO
    settore_3 = db.Column(db.String(50))   # NUOVO CAMPO
    settore_personalizzato = db.Column(db.String(100))  # NUOVO CAMPO
    note = db.Column(db.Text)
    attivo = db.Column(db.Boolean, default=True)
    
    # NUOVO CAMPO PER NUCLEO
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    manutenzioni = db.relationship('Manutenzione', backref='fornitore', lazy=True,
                                 order_by='desc(Manutenzione.data_intervento)')
    veicoli_noleggio = db.relationship('Veicolo', foreign_keys='Veicolo.societa_noleggio_id', 
                                     backref='fornitore_noleggio')
    
    @property
    def settori_lista(self):
        settori = []
        if self.settore:
            settori.append(self.settore)
        if self.settore_2:
            settori.append(self.settore_2)
        if self.settore_3:
            settori.append(self.settore_3)
        if self.settore_personalizzato:
            settori.append(self.settore_personalizzato)
        return settori
    
    @property
    def settori_display(self):
        return ' + '.join(self.settori_lista)

    def __repr__(self):
        return f'<Fornitore {self.ragione_sociale}>'


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
    
    # NUOVO CAMPO PER NUCLEO
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def costo_formattato(self):
        if self.costo:
            return f"€ {self.costo:.2f}"
        return "N/A"

    def __repr__(self):
        return f'<Manutenzione {self.id} - {self.tipo_intervento}>'


class Scadenza(db.Model):
    __tablename__ = 'scadenze'
    
    id = db.Column(db.Integer, primary_key=True)
    veicolo_id = db.Column(db.Integer, db.ForeignKey('veicoli.id'), nullable=False)
    tipo_scadenza = db.Column(db.String(50), nullable=False)
    data_scadenza = db.Column(db.Date, nullable=False)
    costo = db.Column(db.Numeric(10, 2))
    stato = db.Column(db.String(20), default='Attiva')
    note = db.Column(db.Text)
    notifica_giorni = db.Column(db.Integer, default=30)
    
    # NUOVO CAMPO PER NUCLEO
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def giorni_alla_scadenza(self):
        if self.data_scadenza:
            delta = self.data_scadenza - date.today()
            return delta.days
        return None
    
    @property
    def urgente(self):
        giorni = self.giorni_alla_scadenza
        if giorni is not None:
            return giorni <= self.notifica_giorni
        return False
    
    @property
    def costo_formattato(self):
        if self.costo:
            return f"€ {self.costo:.2f}"
        return "N/A"

    def __repr__(self):
        return f'<Scadenza {self.tipo_scadenza} - {self.data_scadenza}>'


# MODELLO USER CON FLASK-LOGIN
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nucleo = db.Column(db.String(50), default='Via Capitel')
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_accesso = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Imposta la password con hash sicuro"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la password"""
        return check_password_hash(self.password_hash, password)
    
    # Metodi richiesti da Flask-Login
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return self.attivo
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'
