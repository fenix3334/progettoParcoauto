from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import Scadenza, Veicolo
from app.forms.scadenze import ScadenzaForm
from app.extensions import db
from datetime import date
from sqlalchemy import and_, text

scadenze_bp = Blueprint('scadenze', __name__)

def clean_field(value):
    """Pulisce i campi opzionali rimuovendo spazi vuoti"""
    if value and value.strip():
        return value.strip()
    return None

def get_scadenze_query():
    """Restituisce query scadenze filtrata per nucleo utente o selezione admin"""
    from flask import session
    
    if current_user.ruolo == 'admin':
        # Admin può filtrare per nucleo specifico o vedere tutte
        filtro_admin = session.get('admin_nucleo_filter', 'tutti')
        
        if filtro_admin == 'tutti':
            # Admin vede tutte le scadenze
            return Scadenza.query
        else:
            # Admin con filtro specifico
            return Scadenza.query.filter_by(nucleo=filtro_admin)
    else:
        # User normale vede solo scadenze del suo nucleo
        return Scadenza.query.filter_by(nucleo=current_user.nucleo)

def get_veicoli_for_choices():
    """Restituisce veicoli per dropdown (filtrati per nucleo)"""
    from flask import session
    
    if current_user.ruolo == 'admin':
        filtro_admin = session.get('admin_nucleo_filter', 'tutti')
        
        if filtro_admin == 'tutti':
            veicoli_query = Veicolo.query
        else:
            veicoli_query = Veicolo.query.filter_by(nucleo=filtro_admin)
    else:
        veicoli_query = Veicolo.query.filter_by(nucleo=current_user.nucleo)
    
    veicoli = veicoli_query.filter_by(stato='Attivo').order_by(Veicolo.targa).all()
    return [(v.id, f"{v.targa} - {v.marca} {v.modello}") for v in veicoli]

def validate_scadenza_access(scadenza_id):
    """Verifica che l'utente possa accedere alla scadenza"""
    scadenza = Scadenza.query.get_or_404(scadenza_id)
    
    if current_user.ruolo == 'admin':
        return scadenza
    
    if scadenza.nucleo != current_user.nucleo:
        abort(403)  # Accesso negato
    
    return scadenza

@scadenze_bp.route('/')
@login_required
def index_scadenze():
    page = request.args.get('page', 1, type=int)
    filtro = request.args.get('filtro', 'tutte')
    
    # Query filtrata per nucleo
    query = get_scadenze_query()
    
    # Applica filtri aggiuntivi
    if filtro == 'urgenti':
        query = query.filter(
            text("date(data_scadenza) <= date('now', '+30 days')")
        ).filter_by(stato='Attiva')
    elif filtro == 'attive':
        query = query.filter_by(stato='Attiva')
    
    scadenze = query.order_by(Scadenza.data_scadenza).paginate(
        page=page, per_page=12, error_out=False  # Più scadenze per pagina visto il layout a card
    )
    
    return render_template('scadenze/index.html', scadenze=scadenze, filtro=filtro)

@scadenze_bp.route('/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_scadenza():
    form = ScadenzaForm()
    
    # Aggiorna choices per veicoli (filtrati per nucleo)
    form.veicolo_id.choices = get_veicoli_for_choices()
    
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
                note=clean_field(form.note.data)
            )
            
            # IMPORTANTE: Imposta automaticamente il nucleo
            veicolo = Veicolo.query.get(form.veicolo_id.data)
            if veicolo:
                scadenza.nucleo = veicolo.nucleo
            else:
                # Fallback: usa nucleo utente
                scadenza.nucleo = current_user.nucleo
            
            db.session.add(scadenza)
            db.session.commit()
            
            flash(f'Scadenza {scadenza.tipo_scadenza} per {scadenza.veicolo.targa} aggiunta con successo!', 'success')
            return redirect(url_for('scadenze.index_scadenze'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
            
    return render_template('scadenze/form.html', form=form, titolo='Aggiungi Scadenza')

@scadenze_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_scadenza(id):
    # Verifica accesso e ottieni scadenza
    scadenza = validate_scadenza_access(id)
    
    form = ScadenzaForm(obj=scadenza)
    
    # Aggiorna choices per veicoli (filtrati per nucleo)
    form.veicolo_id.choices = get_veicoli_for_choices()
    
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
            
            # Aggiorna manualmente i campi
            scadenza.veicolo_id = form.veicolo_id.data
            scadenza.tipo_scadenza = tipo_scadenza_finale
            scadenza.data_scadenza = form.data_scadenza.data
            scadenza.costo = form.costo.data
            scadenza.stato = form.stato.data
            scadenza.notifica_giorni = form.notifica_giorni.data
            scadenza.note = clean_field(form.note.data)
            
            # Aggiorna nucleo se il veicolo è cambiato
            veicolo = Veicolo.query.get(form.veicolo_id.data)
            if veicolo:
                scadenza.nucleo = veicolo.nucleo
            
            db.session.commit()
            flash(f'Scadenza {scadenza.tipo_scadenza} per {scadenza.veicolo.targa} modificata con successo!', 'success')
            return redirect(url_for('scadenze.index_scadenze'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
            
    return render_template('scadenze/form.html', form=form, titolo=f'Modifica Scadenza {scadenza.tipo_scadenza}')

@scadenze_bp.route('/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_scadenza(id):
    # Verifica accesso e ottieni scadenza
    scadenza = validate_scadenza_access(id)
    
    try:
        tipo_scadenza = scadenza.tipo_scadenza
        targa = scadenza.veicolo.targa
        
        db.session.delete(scadenza)
        db.session.commit()
        
        flash(f'Scadenza {tipo_scadenza} per {targa} eliminata con successo!', 'success')
        return redirect(url_for('scadenze.index_scadenze'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
        return redirect(url_for('scadenze.dettaglio_scadenza', id=id))

@scadenze_bp.route('/dettaglio/<int:id>')
@login_required
def dettaglio_scadenza(id):
    # Verifica accesso e ottieni scadenza
    scadenza = validate_scadenza_access(id)
    
    return render_template('scadenze/dettaglio.html', scadenza=scadenza)
