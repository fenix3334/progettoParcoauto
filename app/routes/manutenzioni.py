from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Manutenzione
from app.forms import ManutenzioneForm
from app.extensions import db

manutenzioni_bp = Blueprint('manutenzioni', __name__)

def clean_field(value):
    """Pulisce i campi opzionali rimuovendo spazi vuoti"""
    if value and value.strip():
        return value.strip()
    return None

@manutenzioni_bp.route('/')
@login_required
def index_manutenzioni():
    page = request.args.get('page', 1, type=int)
    manutenzioni = Manutenzione.query.order_by(
        Manutenzione.data_intervento.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    return render_template('manutenzioni/index.html', manutenzioni=manutenzioni)

@manutenzioni_bp.route('/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_manutenzione():
    form = ManutenzioneForm()
    if form.validate_on_submit():
        try:
            manutenzione = Manutenzione(
                veicolo_id=form.veicolo_id.data,
                fornitore_id=form.fornitore_id.data if form.fornitore_id.data else None,
                data_intervento=form.data_intervento.data,
                km_intervento=form.km_intervento.data,
                tipo_intervento=form.tipo_intervento.data,
                stato=form.stato.data,  # NUOVO CAMPO
                descrizione=clean_field(form.descrizione.data),
                costo=form.costo.data,
                numero_fattura=clean_field(form.numero_fattura.data),
                data_fattura=form.data_fattura.data,
                garanzia_mesi=form.garanzia_mesi.data,
                prossima_scadenza_km=form.prossima_scadenza_km.data,
                note=clean_field(form.note.data)
            )
            db.session.add(manutenzione)
            db.session.commit()
            flash(f'Manutenzione per {manutenzione.veicolo.targa} aggiunta con successo!', 'success')
            return redirect(url_for('manutenzioni.index_manutenzioni'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
            
    return render_template('manutenzioni/form.html', form=form, titolo='Aggiungi Manutenzione')

@manutenzioni_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_manutenzione(id):
    manutenzione = Manutenzione.query.get_or_404(id)
    form = ManutenzioneForm(obj=manutenzione)
    
    if form.validate_on_submit():
        try:
            # Aggiorna manualmente i campi per controllo completo
            manutenzione.veicolo_id = form.veicolo_id.data
            manutenzione.fornitore_id = form.fornitore_id.data if form.fornitore_id.data else None
            manutenzione.data_intervento = form.data_intervento.data
            manutenzione.km_intervento = form.km_intervento.data
            manutenzione.tipo_intervento = form.tipo_intervento.data
            manutenzione.stato = form.stato.data  # NUOVO CAMPO
            manutenzione.descrizione = clean_field(form.descrizione.data)
            manutenzione.costo = form.costo.data
            manutenzione.numero_fattura = clean_field(form.numero_fattura.data)
            manutenzione.data_fattura = form.data_fattura.data
            manutenzione.garanzia_mesi = form.garanzia_mesi.data
            manutenzione.prossima_scadenza_km = form.prossima_scadenza_km.data
            manutenzione.note = clean_field(form.note.data)
            
            db.session.commit()
            flash(f'Manutenzione per {manutenzione.veicolo.targa} modificata con successo!', 'success')
            return redirect(url_for('manutenzioni.index_manutenzioni'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
            
    return render_template('manutenzioni/form.html', form=form, titolo='Modifica Manutenzione')

@manutenzioni_bp.route('/elimina/<int:id>')
@login_required
def elimina_manutenzione(id):
    manutenzione = Manutenzione.query.get_or_404(id)
    try:
        targa = manutenzione.veicolo.targa
        tipo_intervento = manutenzione.tipo_intervento
        
        db.session.delete(manutenzione)
        db.session.commit()
        flash(f'Manutenzione {tipo_intervento} per {targa} eliminata con successo!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
        
    return redirect(url_for('manutenzioni.index_manutenzioni'))

@manutenzioni_bp.route('/dettaglio/<int:id>')
@login_required
def dettaglio_manutenzione(id):
    manutenzione = Manutenzione.query.get_or_404(id)
    return render_template('manutenzioni/dettaglio.html', manutenzione=manutenzione)
