from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Optional

class FornitoreForm(FlaskForm):
    ragione_sociale = StringField('Ragione Sociale', validators=[DataRequired(), Length(max=100)])
    partita_iva = StringField('Partita IVA', validators=[Length(max=20)])
    codice_fiscale = StringField('Codice Fiscale', validators=[Length(max=20)])
    indirizzo = StringField('Indirizzo', validators=[Length(max=200)])
    citta = StringField('Città', validators=[DataRequired(), Length(max=50)])
    cap = StringField('CAP', validators=[DataRequired(), Length(max=10)])
    provincia = StringField('Provincia', validators=[Length(max=5)])
    telefono = StringField('Telefono', validators=[Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=100)])
    referente = StringField('Referente', validators=[Length(max=100)])
    settore = SelectField('Settore', 
                         choices=[('Officina', 'Officina'), ('Carrozzeria', 'Carrozzeria'),
                                ('Gommista', 'Gommista'), ('Elettrauto', 'Elettrauto'),
                                ('Carburanti', 'Carburanti'), ('Assicurazioni', 'Assicurazioni'),
                                ('Altro', 'Altro')])
    note = TextAreaField('Note')
    attivo = BooleanField('Attivo', default=True)
