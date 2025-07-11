from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import Manutenzione, Veicolo, Fornitore
from app.forms.manutenzioni import ManutenzioneForm
from app.extensions import db

manutenzioni_bp = Blueprint('manutenzioni', __name__)

def clean_field(value):
    """Pulisce i campi opzionali"""
    if value and value.strip():
        return value.strip()
    return None

def get_manutenzioni_query():
    """Restituisce query manutenzioni filtrata per nucleo utente o selezione admin"""
    from flask import session
    
    if current_user.ruolo == 'admin':
        # Admin può filtrare per nucleo specifico o vedere tutte
        filtro_admin = session.get('admin_nucleo_filter', 'tutti')
        
        if filtro_admin == 'tutti':
            # Admin vede tutte le manutenzioni
            return Manutenzione.query
        else:
            # Admin con filtro specifico
            return Manutenzione.query.filter_by(nucleo=filtro_admin)
    else:
        # User normale vede solo manutenzioni del suo nucleo
        return Manutenzione.query.filter_by(nucleo=current_user.nucleo)

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

def get_fornitori_for_choices():
    """Restituisce fornitori per dropdown (filtrati per nucleo)"""
    from flask import session
    
    if current_user.ruolo == 'admin':
        filtro_admin = session.get('admin_nucleo_filter', 'tutti')
        
        if filtro_admin == 'tutti':
            fornitori_query = Fornitore.query
        else:
            fornitori_query = Fornitore.query.filter_by(nucleo=filtro_admin)
    else:
        fornitori_query = Fornitore.query.filter_by(nucleo=current_user.nucleo)
    
    fornitori = fornitori_query.filter_by(attivo=True).order_by(Fornitore.ragione_sociale).all()
    choices = [('', 'Nessun fornitore')]
    choices.extend([(f.id, f.ragione_sociale) for f in fornitori])
    return choices

def validate_manutenzione_access(manutenzione_id):
    """Verifica che l'utente possa accedere alla manutenzione"""
    manutenzione = Manutenzione.query.get_or_404(manutenzione_id)
    
    if current_user.ruolo == 'admin':
        return manutenzione
    
    if manutenzione.nucleo != current_user.nucleo:
        abort(403)  # Accesso negato
    
    return manutenzione

@manutenzioni_bp.route('/')
@login_required
def index_manutenzioni():
    page = request.args.get('page', 1, type=int)
    
    # Query filtrata per nucleo
    manutenzioni_query = get_manutenzioni_query()
    
    # Filtri aggiuntivi
    stato_filter = request.args.get('stato')  # Cambiato per essere coerente con template
    tipo_filter = request.args.get('tipo')
    
    if stato_filter:
        manutenzioni_query = manutenzioni_query.filter_by(stato=stato_filter)
    
    if tipo_filter:
        manutenzioni_query = manutenzioni_query.filter(
            Manutenzione.tipo_intervento.contains(tipo_filter)
        )
    
    # Ordinamento e paginazione
    manutenzioni = manutenzioni_query.order_by(
        Manutenzione.data_intervento.desc()
    ).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    
    # Informazioni nucleo per l'interfaccia
    from flask import session
    nucleo_corrente = session.get('admin_nucleo_filter', 'tutti') if current_user.ruolo == 'admin' else current_user.nucleo
    nucleo_info = {
        'nome': nucleo_corrente if nucleo_corrente != 'tutti' else 'TUTTI I NUCLEI',
        'is_admin': current_user.ruolo == 'admin',
        'username': current_user.username
    }
    
    # Conta per filtri
    totale_manutenzioni = get_manutenzioni_query().count()
    manutenzioni_da_fare = get_manutenzioni_query().filter_by(stato='Da Fare').count()
    
    return render_template('manutenzioni/index.html', 
                         manutenzioni=manutenzioni,
                         nucleo_info=nucleo_info,
                         totale_manutenzioni=totale_manutenzioni,
                         manutenzioni_da_fare=manutenzioni_da_fare,
                         stato_filter=stato_filter,  # Coerente con template
                         tipo_filter=tipo_filter)

@manutenzioni_bp.route('/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_manutenzione():
    form = ManutenzioneForm()
    
    # Aggiorna choices per veicoli e fornitori (filtrati per nucleo)
    form.veicolo_id.choices = get_veicoli_for_choices()
    form.fornitore_id.choices = get_fornitori_for_choices()
    
    if form.validate_on_submit():
        try:
            manutenzione = Manutenzione(
                veicolo_id=form.veicolo_id.data,
                fornitore_id=form.fornitore_id.data if form.fornitore_id.data else None,
                data_intervento=form.data_intervento.data,
                km_intervento=form.km_intervento.data,
                tipo_intervento=form.tipo_intervento.data,
                descrizione=clean_field(form.descrizione.data),
                costo=form.costo.data,
                numero_fattura=clean_field(form.numero_fattura.data),
                data_fattura=form.data_fattura.data,
                garanzia_mesi=form.garanzia_mesi.data,
                prossima_scadenza_km=form.prossima_scadenza_km.data,
                stato=form.stato.data,
                note=clean_field(form.note.data)
            )
            
            # IMPORTANTE: Imposta automaticamente il nucleo
            veicolo = Veicolo.query.get(form.veicolo_id.data)
            if veicolo:
                manutenzione.nucleo = veicolo.nucleo
            else:
                # Fallback: usa nucleo utente
                manutenzione.nucleo = current_user.nucleo
            
            db.session.add(manutenzione)
            db.session.commit()
            
            flash(f'Manutenzione {manutenzione.tipo_intervento} per {manutenzione.veicolo.targa} aggiunta con successo!', 'success')
            return redirect(url_for('manutenzioni.index_manutenzioni'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
    
    return render_template('manutenzioni/form.html', form=form, titolo='Aggiungi Manutenzione')

@manutenzioni_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_manutenzione(id):
    # Verifica accesso e ottieni manutenzione
    manutenzione = validate_manutenzione_access(id)
    
    form = ManutenzioneForm(obj=manutenzione)
    
    # Aggiorna choices per veicoli e fornitori (filtrati per nucleo)
    form.veicolo_id.choices = get_veicoli_for_choices()
    form.fornitore_id.choices = get_fornitori_for_choices()
    
    if form.validate_on_submit():
        try:
            manutenzione.veicolo_id = form.veicolo_id.data
            manutenzione.fornitore_id = form.fornitore_id.data if form.fornitore_id.data else None
            manutenzione.data_intervento = form.data_intervento.data
            manutenzione.km_intervento = form.km_intervento.data
            manutenzione.tipo_intervento = form.tipo_intervento.data
            manutenzione.descrizione = clean_field(form.descrizione.data)
            manutenzione.costo = form.costo.data
            manutenzione.numero_fattura = clean_field(form.numero_fattura.data)
            manutenzione.data_fattura = form.data_fattura.data
            manutenzione.garanzia_mesi = form.garanzia_mesi.data
            manutenzione.prossima_scadenza_km = form.prossima_scadenza_km.data
            manutenzione.stato = form.stato.data
            manutenzione.note = clean_field(form.note.data)
            
            # Aggiorna nucleo se il veicolo è cambiato
            veicolo = Veicolo.query.get(form.veicolo_id.data)
            if veicolo:
                manutenzione.nucleo = veicolo.nucleo
            
            db.session.commit()
            flash(f'Manutenzione {manutenzione.tipo_intervento} per {manutenzione.veicolo.targa} modificata con successo!', 'success')
            return redirect(url_for('manutenzioni.index_manutenzioni'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
    
    return render_template('manutenzioni/form.html', 
                         form=form, 
                         titolo=f'Modifica Manutenzione {manutenzione.tipo_intervento}')

@manutenzioni_bp.route('/dettaglio/<int:id>')
@login_required
def dettaglio_manutenzione(id):
    # Verifica accesso e ottieni manutenzione
    manutenzione = validate_manutenzione_access(id)
    
    return render_template('manutenzioni/dettaglio.html', manutenzione=manutenzione)

@manutenzioni_bp.route('/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_manutenzione(id):
    # Verifica accesso e ottieni manutenzione
    manutenzione = validate_manutenzione_access(id)
    
    try:
        tipo_intervento = manutenzione.tipo_intervento
        targa = manutenzione.veicolo.targa
        
        db.session.delete(manutenzione)
        db.session.commit()
        
        flash(f'Manutenzione {tipo_intervento} per {targa} eliminata con successo!', 'success')
        return redirect(url_for('manutenzioni.index_manutenzioni'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
        return redirect(url_for('manutenzioni.dettaglio_manutenzione', id=id))
