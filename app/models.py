from app.extensions import db
from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# MODELLO PER GESTIONE NUCLEI DINAMICA
class Nucleo(db.Model):
    __tablename__ = 'nuclei'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descrizione = db.Column(db.String(200))
    indirizzo = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Nucleo {self.nome}>'

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
    carburante_personalizzato = db.Column(db.String(50))
    cilindrata = db.Column(db.Integer)
    colore = db.Column(db.String(30))
    stato = db.Column(db.String(20), default='Attivo')
    note = db.Column(db.Text)
    
    # CAMPI PER CARTA CARBURANTE
    carta_carburante = db.Column(db.String(100))
    pin_carburante = db.Column(db.String(20))
    
    # CAMPO PER SOCIETÀ NOLEGGIO
    societa_noleggio_id = db.Column(db.Integer, db.ForeignKey('fornitori.id'))
    
    # CAMPO NUCLEO
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    # 🆕 NUOVO CAMPO UNITÀ OPERATIVA
    unita_operativa = db.Column(db.String(100), default='Cure Primarie ADI Via del Capitel')
    unita_operativa_personalizzata = db.Column(db.String(100))  # Per opzione "Altro"
    
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
    
    @property
    def unita_operativa_display(self):
        """Restituisce l'unità operativa da visualizzare (personalizzata o predefinita)"""
        return self.unita_operativa_personalizzata if self.unita_operativa_personalizzata else self.unita_operativa

    def __repr__(self):
        return f'<Veicolo {self.targa}>'


class Fornitore(db.Model):
    __tablename__ = 'fornitori'
    
    id = db.Column(db.Integer, primary_key=True)
    ragione_sociale = db.Column(db.String(200), nullable=False)
    partita_iva = db.Column(db.String(11), unique=True, nullable=True)
    codice_fiscale = db.Column(db.String(16))
    indirizzo = db.Column(db.String(200))
    citta = db.Column(db.String(100))
    cap = db.Column(db.String(5))
    provincia = db.Column(db.String(2))
    
    # TELEFONI MULTIPLI
    telefono = db.Column(db.String(20))
    telefono_2 = db.Column(db.String(20))
    telefono_3 = db.Column(db.String(20))
    
    # EMAIL MULTIPLE
    email = db.Column(db.String(100))
    email_2 = db.Column(db.String(100))
    email_3 = db.Column(db.String(100))
    
    referente = db.Column(db.String(100))
    
    # SETTORI MULTIPLI
    settore = db.Column(db.String(100))
    settore_2 = db.Column(db.String(100))
    settore_3 = db.Column(db.String(100))
    settore_personalizzato = db.Column(db.String(100))
    
    # CAMPO NUCLEO
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    note = db.Column(db.Text)
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relazioni
    manutenzioni = db.relationship('Manutenzione', backref='fornitore', lazy=True)
    
    def clean_field(self, value):
        """Pulisce i campi opzionali"""
        if value and value.strip():
            return value.strip()
        return None
    
    @property
    def telefoni_lista(self):
        telefoni = []
        if self.telefono: telefoni.append(self.telefono)
        if self.telefono_2: telefoni.append(self.telefono_2)
        if self.telefono_3: telefoni.append(self.telefono_3)
        return telefoni
    
    @property
    def email_lista(self):
        emails = []
        if self.email: emails.append(self.email)
        if self.email_2: emails.append(self.email_2)
        if self.email_3: emails.append(self.email_3)
        return emails
    
    @property
    def settori_lista(self):
        settori = []
        if self.settore: settori.append(self.settore)
        if self.settore_2: settori.append(self.settore_2)
        if self.settore_3: settori.append(self.settore_3)
        if self.settore_personalizzato: settori.append(self.settore_personalizzato)
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
    
    # CAMPO PER FLAG FATTO/DA FARE
    stato = db.Column(db.String(20), default='Da Fare')
    
    # CAMPO NUCLEO
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
    
    # NOTIFICHE
    notifica_giorni = db.Column(db.Integer, default=30)
    
    # CAMPO NUCLEO
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def costo_formattato(self):
        if self.costo:
            return f"€ {self.costo:.2f}"
        return "N/A"
    
    @property
    def giorni_scadenza(self):
        """Calcola i giorni alla scadenza"""
        if self.data_scadenza:
            delta = self.data_scadenza - date.today()
            return delta.days
        return None
    
    @property
    def stato_urgenza(self):
        """Determina lo stato di urgenza"""
        giorni = self.giorni_scadenza
        if giorni is None:
            return 'sconosciuto'
        elif giorni < 0:
            return 'scaduta'
        elif giorni <= 7:
            return 'critica'
        elif giorni <= 30:
            return 'urgente'
        else:
            return 'normale'

    def __repr__(self):
        return f'<Scadenza {self.id} - {self.tipo_scadenza}>'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    # CAMPO NUCLEO - DETERMINA QUALI DATI PUÒ VEDERE
    nucleo = db.Column(db.String(50), default='Via Capitel')
    
    # CAMPO RUOLO - ADMIN PUÒ VEDERE TUTTI I NUCLEI
    ruolo = db.Column(db.String(20), default='user')  # 'user' o 'admin'
    
    attivo = db.Column(db.Boolean, default=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_accesso = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        """Controlla se l'utente è admin"""
        return self.ruolo == 'admin'
    
    def can_see_nucleo(self, nucleo_nome):
        """Controlla se l'utente può vedere dati di un nucleo"""
        if self.is_admin:
            return True
        return self.nucleo == nucleo_nome
    
    def get_nuclei_visibili(self):
        """Restituisce lista nuclei che l'utente può vedere"""
        if self.is_admin:
            return Nucleo.query.filter_by(attivo=True).all()
        else:
            return Nucleo.query.filter_by(nome=self.nucleo, attivo=True).all()

    def __repr__(self):
        return f'<User {self.username}>'


class SocietaNoleggio(db.Model):
    __tablename__ = 'societa_noleggio'
    
    id = db.Column(db.Integer, primary_key=True)
    ragione_sociale = db.Column(db.String(200), nullable=False)
    partita_iva = db.Column(db.String(11))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    indirizzo = db.Column(db.String(200))
    note = db.Column(db.Text)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SocietaNoleggio {self.ragione_sociale}>'
