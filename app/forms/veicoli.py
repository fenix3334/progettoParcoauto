from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import date
from app.models import Fornitore

class VeicoloForm(FlaskForm):
    # CAMPI BASE (già esistenti)
    targa = StringField('Targa', validators=[DataRequired(), Length(max=10)])
    marca = StringField('Marca', validators=[DataRequired(), Length(max=50)])
    modello = StringField('Modello', validators=[DataRequired(), Length(max=50)])
    anno_immatricolazione = IntegerField('Anno Immatricolazione', 
                                       validators=[DataRequired(), NumberRange(min=1950, max=date.today().year)])
    data_immatricolazione = DateField('Data Immatricolazione', validators=[DataRequired()])
    km_attuali = IntegerField('KM Attuali', validators=[NumberRange(min=0)], default=0)
    
    # CARBURANTE CON OPZIONE PERSONALIZZATA
    carburante = SelectField('Carburante', 
                           choices=[
                               ('Benzina', 'Benzina'), 
                               ('Diesel', 'Diesel'), 
                               ('GPL', 'GPL'), 
                               ('Metano', 'Metano'), 
                               ('Elettrico', 'Elettrico'), 
                               ('Ibrido', 'Ibrido'),
                               ('Personalizzato', 'Altro (specifica sotto)')
                           ],
                           validators=[DataRequired()])
    
    # NUOVO: Carburante personalizzato
    carburante_personalizzato = StringField(
        'Carburante Personalizzato', 
        validators=[Optional(), Length(max=50)],
        render_kw={'placeholder': 'Es: Idrogeno, Biocarburante, ecc.'}
    )
    
    cilindrata = IntegerField('Cilindrata (cc)', validators=[Optional(), NumberRange(min=50, max=8000)])
    colore = StringField('Colore', validators=[Optional(), Length(max=30)])
    
    stato = SelectField('Stato', 
                       choices=[
                           ('Attivo', 'Attivo'), 
                           ('Inattivo', 'Inattivo'), 
                           ('In manutenzione', 'In manutenzione'), 
                           ('Venduto', 'Venduto')
                       ],
                       default='Attivo')
    
    # NUOVI CAMPI: Carta carburante
    carta_carburante = StringField(
        'Carta Carburante', 
        validators=[Optional(), Length(max=100)],
        render_kw={'placeholder': 'Es: Tamoil Fleet, Eni Card, ecc.'}
    )
    
    pin_carburante = StringField(
        'PIN Carta Carburante', 
        validators=[Optional(), Length(max=20)],
        render_kw={'placeholder': 'PIN della carta carburante'}
    )
    
    # NUOVO: Società di noleggio
    societa_noleggio_id = SelectField(
        'Società di Noleggio', 
        choices=[('', 'Nessuna (veicolo di proprietà)')],
        validators=[Optional()],
        coerce=lambda x: int(x) if x else None
    )
    
    # NUOVO: Nucleo di appartenenza
    nucleo = SelectField(
        'Nucleo', 
        choices=[
            ('Via Capitel', 'Via Capitel'), 
            ('Campania', 'Campania')
        ],
        default='Via Capitel',
        validators=[DataRequired()]
    )
    
    note = TextAreaField('Note', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(VeicoloForm, self).__init__(*args, **kwargs)
        
        # Carica dinamicamente le società di noleggio dai fornitori
        from app.models import Fornitore
        societa_noleggio = Fornitore.query.filter(
            Fornitore.settore.contains('noleggio')
        ).all()
