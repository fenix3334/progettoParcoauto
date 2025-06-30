from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import date
from app.models import Fornitore

class VeicoloForm(FlaskForm):
    # CAMPI BASE
    targa = StringField('Targa', validators=[DataRequired(), Length(max=10)])
    marca = StringField('Marca', validators=[DataRequired(), Length(max=50)])
    modello = StringField('Modello', validators=[DataRequired(), Length(max=50)])
    anno_immatricolazione = IntegerField('Anno Immatricolazione', 
                                       validators=[DataRequired(), NumberRange(min=1950, max=date.today().year)])
    data_immatricolazione = DateField('Data Immatricolazione', validators=[DataRequired()])
    km_attuali = IntegerField('KM Attuali', validators=[NumberRange(min=0)], default=0)
    
    # CARBURANTE
    carburante = SelectField('Carburante', 
                           choices=[('Benzina', 'Benzina'), ('Diesel', 'Diesel'), 
                                  ('GPL', 'GPL'), ('Metano', 'Metano'), ('Elettrico', 'Elettrico'), 
                                  ('Ibrido', 'Ibrido'), ('Personalizzato', 'Personalizzato')],
                           validators=[DataRequired()])
    
    carburante_personalizzato = StringField('Carburante Personalizzato', 
                                          validators=[Optional(), Length(max=50)])
    
    cilindrata = IntegerField('Cilindrata (cc)', validators=[Optional(), NumberRange(min=50, max=8000)])
    colore = StringField('Colore', validators=[Optional(), Length(max=30)])
    
    stato = SelectField('Stato', 
                       choices=[('Attivo', 'Attivo'), ('Inattivo', 'Inattivo'), 
                              ('In manutenzione', 'In manutenzione'), ('Venduto', 'Venduto')],
                       default='Attivo')
    
    # INFORMAZIONI CARTA CARBURANTE
    carta_carburante = StringField('Numero Carta Carburante', 
                                  validators=[Optional(), Length(max=100)])
    pin_carburante = StringField('PIN Carta', 
                               validators=[Optional(), Length(max=20)])
    
    # SOCIETÀ NOLEGGIO
    societa_noleggio_id = SelectField('Società Noleggio',
                                    coerce=lambda x: int(x) if x else None,
                                    validators=[Optional()])
    
    # NUCLEO
    nucleo = SelectField('Nucleo',
                        choices=[('Via Capitel', 'Via Capitel'), 
                               ('Campania', 'Campania')],
                        default='Via Capitel',
                        validators=[DataRequired()])
    
    note = TextAreaField('Note')
    
    def __init__(self, *args, **kwargs):
        super(VeicoloForm, self).__init__(*args, **kwargs)
        
        # Popola le società di noleggio (fornitori con settore "Società noleggio" o "Leasing")
        societa_choices = [('', 'Nessuna (veicolo di proprietà)')]
        
        # Cerca fornitori che sono società di noleggio o leasing
        fornitori_noleggio = Fornitore.query.filter(Fornitore.attivo == True).all()
        
        # Filtra quelli che hanno "noleggio" o "leasing" in uno dei settori
        for fornitore in fornitori_noleggio:
            settori_completi = [
                fornitore.settore or '',
                fornitore.settore_2 or '',
                fornitore.settore_3 or '',
                fornitore.settore_personalizzato or ''
            ]
            
            # Controlla se uno dei settori contiene "noleggio" o "leasing"
            è_noleggio = any(
                'noleggio' in settore.lower() or 'leasing' in settore.lower()
                for settore in settori_completi
                if settore
            )
            
            if è_noleggio:
                societa_choices.append((fornitore.id, fornitore.ragione_sociale))
        self.societa_noleggio_id.choices = societa_choices
