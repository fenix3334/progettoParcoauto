from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional

class FornitoreForm(FlaskForm):
    ragione_sociale = StringField('Ragione Sociale', validators=[DataRequired(), Length(max=100)])
    
    # SETTORI MULTIPLI
    settore = SelectField('Settore Principale', 
                         choices=[
                             ('', 'Seleziona settore...'),
                             ('Officina', 'Officina'),
                             ('Gommista', 'Gommista'), 
                             ('Carrozzeria', 'Carrozzeria'),
                             ('Elettrauto', 'Elettrauto'),
                             ('Concessionario', 'Concessionario'),
                             ('Società noleggio', 'Società noleggio'),
                             ('Assicurazione', 'Assicurazione'),
                             ('Assistenza stradale', 'Assistenza stradale'),
                             ('Carburanti', 'Distributore carburante'),
                             ('Autolavaggio', 'Autolavaggio'),
                             ('Pneumatici', 'Pneumatici'),
                             ('Revisioni', 'Centro revisioni'),
                             ('Ricambi', 'Ricambi auto'),
                             ('Consulenza', 'Consulenza automotive'),
                             ('Finanziaria', 'Finanziaria/Leasing'),
                             ('Altro', 'Altro')
                         ],
                         validators=[Optional()])
    
    settore_2 = SelectField('Settore Secondario', 
                           choices=[
                               ('', 'Nessuno'),
                               ('Officina', 'Officina'),
                               ('Gommista', 'Gommista'), 
                               ('Carrozzeria', 'Carrozzeria'),
                               ('Elettrauto', 'Elettrauto'),
                               ('Concessionario', 'Concessionario'),
                               ('Società noleggio', 'Società noleggio'),
                               ('Assicurazione', 'Assicurazione'),
                               ('Assistenza stradale', 'Assistenza stradale'),
                               ('Carburanti', 'Distributore carburante'),
                               ('Autolavaggio', 'Autolavaggio'),
                               ('Pneumatici', 'Pneumatici'),
                               ('Revisioni', 'Centro revisioni'),
                               ('Ricambi', 'Ricambi auto'),
                               ('Consulenza', 'Consulenza automotive'),
                               ('Finanziaria', 'Finanziaria/Leasing'),
                               ('Altro', 'Altro')
                           ],
                           validators=[Optional()])
    
    settore_3 = SelectField('Settore Terziario', 
                           choices=[
                               ('', 'Nessuno'),
                               ('Officina', 'Officina'),
                               ('Gommista', 'Gommista'), 
                               ('Carrozzeria', 'Carrozzeria'),
                               ('Elettrauto', 'Elettrauto'),
                               ('Concessionario', 'Concessionario'),
                               ('Società noleggio', 'Società noleggio'),
                               ('Assicurazione', 'Assicurazione'),
                               ('Assistenza stradale', 'Assistenza stradale'),
                               ('Carburanti', 'Distributore carburante'),
                               ('Autolavaggio', 'Autolavaggio'),
                               ('Pneumatici', 'Pneumatici'),
                               ('Revisioni', 'Centro revisioni'),
                               ('Ricambi', 'Ricambi auto'),
                               ('Consulenza', 'Consulenza automotive'),
                               ('Finanziaria', 'Finanziaria/Leasing'),
                               ('Altro', 'Altro')
                           ],
                           validators=[Optional()])
    
    settore_personalizzato = StringField(
        'Settore Personalizzato', 
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Specifica settore se hai selezionato "Altro"'}
    )
    
    # DATI FISCALI
    partita_iva = StringField('Partita IVA', validators=[Optional(), Length(max=20)])
    codice_fiscale = StringField('Codice Fiscale', validators=[Optional(), Length(max=20)])
    
    # INDIRIZZO
    indirizzo = StringField('Indirizzo', validators=[Optional(), Length(max=200)])
    citta = StringField('Città', validators=[DataRequired(), Length(max=50)])
    cap = StringField('CAP', validators=[DataRequired(), Length(max=10)])
    provincia = StringField('Provincia', validators=[Optional(), Length(max=5)])
    
    # CONTATTI MULTIPLI
    telefono = StringField('Telefono Principale', validators=[Optional(), Length(max=20)])
    telefono_2 = StringField('Telefono 2', validators=[Optional(), Length(max=20)])
    telefono_3 = StringField('Telefono 3', validators=[Optional(), Length(max=20)])
    
    email = StringField('Email Principale', validators=[Optional(), Email(), Length(max=100)])
    email_2 = StringField('Email 2', validators=[Optional(), Email(), Length(max=100)])
    email_3 = StringField('Email 3', validators=[Optional(), Email(), Length(max=100)])
    
    referente = StringField('Referente', validators=[Optional(), Length(max=100)])
    
    # NUCLEO
    nucleo = SelectField('Nucleo', 
                        choices=[
                            ('Via Capitel', 'Via Capitel'), 
                            ('Campania', 'Campania')
                        ],
                        default='Via Capitel',
                        validators=[DataRequired()])
    
    note = TextAreaField('Note', validators=[Optional()])
    attivo = BooleanField('Attivo', default=True)
