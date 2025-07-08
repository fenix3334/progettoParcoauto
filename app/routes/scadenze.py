from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Scadenza
from app.forms import ScadenzaForm
from app.extensions import db
from datetime import date

scadenze_bp = Blueprint('scadenze', __name__)

def clean_field(value):
    """Pulisce i campi opzionali rimuovendo spazi vuoti"""
    if value and value.strip():
        return value.strip()
    return None

@scadenze_bp.route('/')
def index_scadenze():
    page = request.args.get('page', 1, type=int)
    filtro = request.args.get('filtro', 'tutte')
    
    query = Scadenza.query
    
    if filtro == 'urgenti':
        query = query.filter(Scadenza.data_scadenza <= date.today())
    elif filtro == 'attive':
        query = query.filter_by(stato='Attiva')
    
    scadenze = query.order_by(Scadenza.data_scadenza).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('scadenze/index.html', scadenze=scadenze, filtro=filtro)

@scadenze_bp.route('/aggiungi', methods=['GET', 'POST'])
def aggiungi_scadenza():
    form = ScadenzaForm()
    if form.validate_on_submit():
        try:
            # GESTIONE TIPO SCADENZA PERSONALIZZATO
            tipo_scadenza_finale = form.tipo_scadenza.data
            if form.tipo_scadenza.data == 'Altro' and form.tipo_scadenza_personalizzato.data:
                tipo_scadenza_finale = clean_field(form.tipo_scadenza_personalizzato.data)
            
            scadenza = Scadenza(
                veicolo_id=form.veicolo_id.data,
                tipo_scadenza=tipo_scadenza_finale,
                data_scadenza=form.data_scadenza.data,
                costo=form.costo.data,
                stato=form.stato.data,
                notifica_giorni=form.notifica_giorni.data,
                note=form.note.data
            )
            db.session.add(scadenza)
            db.session.commit()
            flash(f'Scadenza {scadenza.tipo_scadenza} per {scadenza.veicolo.targa} aggiunta con successo!', 'success')
            return redirect(url_for('scadenze.index_scadenze'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
            
    return render_template('scadenze/form.html', form=form, titolo='Aggiungi Scadenza')

@scadenze_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_scadenza(id):
    scadenza = Scadenza.query.get_or_404(id)
    form = ScadenzaForm(obj=scadenza)
    
    # Se in modifica e il tipo_scadenza non è tra le opzioni predefinite, 
    # impostalo come "Altro" e popola il campo personalizzato
    opzioni_predefinite = ['Revisione', 'Assicurazione', 'Bollo', 'Tagliando', 
                          'Controllo gas di scarico', 'Consegna auto a noleggio', 
                          'Riconsegna auto da noleggio']
    
    if request.method == 'GET' and scadenza.tipo_scadenza not in opzioni_predefinite:
        form.tipo_scadenza.data = 'Altro'
        form.tipo_scadenza_personalizzato.data = scadenza.tipo_scadenza
    
    if form.validate_on_submit():
        try:
            # GESTIONE TIPO SCADENZA PERSONALIZZATO
            tipo_scadenza_finale = form.tipo_scadenza.data
            if form.tipo_scadenza.data == 'Altro' and form.tipo_scadenza_personalizzato.data:
                tipo_scadenza_finale = clean_field(form.tipo_scadenza_personalizzato.data)
            
            # Aggiorna manualmente i campi (invece di populate_obj per controllo completo)
            scadenza.veicolo_id = form.veicolo_id.data
            scadenza.tipo_scadenza = tipo_scadenza_finale
            scadenza.data_scadenza = form.data_scadenza.data
            scadenza.costo = form.costo.data
            scadenza.stato = form.stato.data
            scadenza.notifica_giorni = form.notifica_giorni.data
            scadenza.note = form.note.data
            
            db.session.commit()
            flash(f'Scadenza {scadenza.tipo_scadenza} per {scadenza.veicolo.targa} modificata con successo!', 'success')
            return redirect(url_for('scadenze.index_scadenze'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
            
    return render_template('scadenze/form.html', form=form, titolo='Modifica Scadenza')

@scadenze_bp.route('/elimina/<int:id>')
def elimina_scadenza(id):
    scadenza = Scadenza.query.get_or_404(id)
    db.session.delete(scadenza)
    db.session.commit()
    flash(f'Scadenza {scadenza.tipo_scadenza} per {scadenza.veicolo.targa} eliminata con successo!', 'success')
    return redirect(url_for('scadenze.index_scadenze'))

@scadenze_bp.route('/dettaglio/<int:id>')
def dettaglio_scadenza(id):
    scadenza = Scadenza.query.get_or_404(id)
    return render_template('scadenze/dettaglio.html', scadenza=scadenza)
