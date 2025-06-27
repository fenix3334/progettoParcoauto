from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange
from datetime import date

class VeicoloForm(FlaskForm):
    targa = StringField('Targa', validators=[DataRequired(), Length(max=10)])
    marca = StringField('Marca', validators=[DataRequired(), Length(max=50)])
    modello = StringField('Modello', validators=[DataRequired(), Length(max=50)])
    anno_immatricolazione = IntegerField('Anno Immatricolazione', 
                                       validators=[DataRequired(), NumberRange(min=1950, max=date.today().year)])
    data_immatricolazione = DateField('Data Immatricolazione', validators=[DataRequired()])
    km_attuali = IntegerField('KM Attuali', validators=[NumberRange(min=0)], default=0)
    carburante = SelectField('Carburante', 
                           choices=[('Benzina', 'Benzina'), ('Diesel', 'Diesel'), 
                                  ('GPL', 'GPL'), ('Metano', 'Metano'), ('Elettrico', 'Elettrico'), 
                                  ('Ibrido', 'Ibrido')],
                           validators=[DataRequired()])
    cilindrata = IntegerField('Cilindrata (cc)', validators=[NumberRange(min=50, max=8000)])
    colore = StringField('Colore', validators=[Length(max=30)])
    stato = SelectField('Stato', 
                       choices=[('Attivo', 'Attivo'), ('Inattivo', 'Inattivo'), 
                              ('In manutenzione', 'In manutenzione'), ('Venduto', 'Venduto')],
                       default='Attivo')
    note = TextAreaField('Note')
