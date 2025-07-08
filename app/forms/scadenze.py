from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, StringField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Optional, Length
from app.models import Veicolo

class ScadenzaForm(FlaskForm):
    veicolo_id = SelectField('Veicolo', coerce=int, validators=[DataRequired()])
    tipo_scadenza = SelectField('Tipo Scadenza',
                              choices=[('Revisione', 'Revisione'), ('Assicurazione', 'Assicurazione'),
                                     ('Bollo', 'Bollo'), ('Tagliando', 'Tagliando'),
                                     ('Controllo gas di scarico', 'Controllo gas di scarico'),
                                     ('Consegna auto a noleggio', 'Consegna auto a noleggio'),
                                     ('Riconsegna auto da noleggio', 'Riconsegna auto da noleggio'),
                                     ('Altro', 'Altro')],
                              validators=[DataRequired()])
    
    # NUOVO CAMPO PER SCADENZA PERSONALIZZATA
    tipo_scadenza_personalizzato = StringField('Tipo Scadenza Personalizzato', 
                                             validators=[Optional(), Length(max=100)])
    
    data_scadenza = DateField('Data Scadenza', validators=[DataRequired()])
    costo = DecimalField('Costo (€)', validators=[Optional(), NumberRange(min=0)], places=2)
    stato = SelectField('Stato',
                       choices=[('Attiva', 'Attiva'), ('Scaduta', 'Scaduta'), ('Rinnovata', 'Rinnovata')],
                       default='Attiva')
    notifica_giorni = IntegerField('Notifica (giorni prima)', validators=[NumberRange(min=1, max=365)], default=30)
    note = TextAreaField('Note')
    
    def __init__(self, *args, **kwargs):
        super(ScadenzaForm, self).__init__(*args, **kwargs)
        self.veicolo_id.choices = [(v.id, f"{v.targa} - {v.marca} {v.modello}") 
                                  for v in Veicolo.query.all()]
