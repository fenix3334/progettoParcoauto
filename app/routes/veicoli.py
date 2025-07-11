from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import Veicolo, Fornitore, SocietaNoleggio
from app.forms.veicoli import VeicoloForm
from app.extensions import db
from sqlalchemy import and_

# Importa utility per gestione nuclei
from app.utils.nuclei import (
    get_veicoli_by_nucleo, 
    get_fornitori_for_choices,
    get_societa_noleggio_for_choices,
    can_access_record,
    should_filter_by_nucleo,
    get_nucleo_corrente_admin
)

veicoli_bp = Blueprint('veicoli', __name__)

def clean_field(value):
    """Pulisce i campi opzionali"""
    if value and value.strip():
        return value.strip()
    return None

def validate_veicolo_access(veicolo_id):
    """Verifica che l'utente possa accedere al veicolo"""
    veicolo = Veicolo.query.get_or_404(veicolo_id)
    
    if not can_access_record(veicolo):
        abort(403)  # Accesso negato
    
    return veicolo

@veicoli_bp.route('/')
@login_required
def index_veicoli():
    page = request.args.get('page', 1, type=int)
    
    # Query filtrata per nucleo usando utility
    veicoli_query = get_veicoli_by_nucleo()
    
    # Filtri aggiuntivi
    stato_filter = request.args.get('stato')
    carburante_filter = request.args.get('carburante')
    
    if stato_filter:
        veicoli_query = veicoli_query.filter_by(stato=stato_filter)
    
    if carburante_filter:
        veicoli_query = veicoli_query.filter_by(carburante=carburante_filter)
    
    # Ordinamento e paginazione
    veicoli = veicoli_query.order_by(Veicolo.targa).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    
    # Informazioni nucleo per l'interfaccia
    nucleo_corrente = get_nucleo_corrente_admin()
    nucleo_info = {
        'nome': nucleo_corrente if nucleo_corrente else 'TUTTI I NUCLEI',
        'is_admin': current_user.ruolo == 'admin',
        'username': current_user.username,
        'filtro_attivo': should_filter_by_nucleo()
    }
    
    # Conta per filtri
    totale_veicoli = get_veicoli_by_nucleo().count()
    veicoli_attivi = get_veicoli_by_nucleo().filter_by(stato='Attivo').count()
    
    return render_template('veicoli/index.html', 
                         veicoli=veicoli,
                         nucleo_info=nucleo_info,
                         totale_veicoli=totale_veicoli,
                         veicoli_attivi=veicoli_attivi,
                         stato_filter=stato_filter,
                         carburante_filter=carburante_filter)

@veicoli_bp.route('/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_veicolo():
    form = VeicoloForm()
    
    # Aggiorna choices per società noleggio (filtrate per nucleo)
    form.societa_noleggio_id.choices = get_societa_noleggio_for_choices()
    
    if form.validate_on_submit():
        try:
            veicolo = Veicolo(
                targa=form.targa.data.upper(),
                marca=form.marca.data,
                modello=form.modello.data,
                anno_immatricolazione=form.anno_immatricolazione.data,
                data_immatricolazione=form.data_immatricolazione.data,
                km_attuali=form.km_attuali.data,
                carburante=form.carburante.data,
                carburante_personalizzato=clean_field(form.carburante_personalizzato.data),
                cilindrata=form.cilindrata.data,
                colore=clean_field(form.colore.data),
                carta_carburante=clean_field(form.carta_carburante.data),
                pin_carburante=clean_field(form.pin_carburante.data),
                societa_noleggio_id=form.societa_noleggio_id.data if form.societa_noleggio_id.data else None,
                stato=form.stato.data,
                note=clean_field(form.note.data)
            )
            
            # IMPORTANTE: Imposta automaticamente il nucleo
            nucleo_target = get_nucleo_corrente_admin()
            if current_user.ruolo == 'admin' and nucleo_target:
                # Admin con filtro specifico
                veicolo.nucleo = nucleo_target
            elif current_user.ruolo == 'admin':
                # Admin senza filtro: usa nucleo predefinito
                veicolo.nucleo = 'Via Capitel'  # O chiedi all'admin
            else:
                # User normale: nucleo automatico
                veicolo.nucleo = current_user.nucleo
            
            db.session.add(veicolo)
            db.session.commit()
            
            flash(f'Veicolo {veicolo.targa} aggiunto con successo al nucleo {veicolo.nucleo}!', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
    
    nucleo_corrente = get_nucleo_corrente_admin() or current_user.nucleo
    return render_template('veicoli/form.html', 
                         form=form, 
                         titolo='Aggiungi Veicolo',
                         nucleo_corrente=nucleo_corrente)

@veicoli_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_veicolo(id):
    # Verifica accesso e ottieni veicolo
    veicolo = validate_veicolo_access(id)
    
    form = VeicoloForm(obj=veicolo)
    
    # Aggiorna choices per società noleggio (filtrate per nucleo)
    form.societa_noleggio_id.choices = get_societa_noleggio_for_choices()
    
    if form.validate_on_submit():
        try:
            veicolo.targa = form.targa.data.upper()
            veicolo.marca = form.marca.data
            veicolo.modello = form.modello.data
            veicolo.anno_immatricolazione = form.anno_immatricolazione.data
            veicolo.data_immatricolazione = form.data_immatricolazione.data
            veicolo.km_attuali = form.km_attuali.data
            veicolo.carburante = form.carburante.data
            veicolo.carburante_personalizzato = clean_field(form.carburante_personalizzato.data)
            veicolo.cilindrata = form.cilindrata.data
            veicolo.colore = clean_field(form.colore.data)
            veicolo.carta_carburante = clean_field(form.carta_carburante.data)
            veicolo.pin_carburante = clean_field(form.pin_carburante.data)
            veicolo.societa_noleggio_id = form.societa_noleggio_id.data if form.societa_noleggio_id.data else None
            veicolo.stato = form.stato.data
            veicolo.note = clean_field(form.note.data)
            
            # SICUREZZA: Solo admin può cambiare nucleo (se implementiamo campo nella form)
            # Per ora il nucleo rimane invariato
            
            db.session.commit()
            flash(f'Veicolo {veicolo.targa} modificato con successo!', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
    
    return render_template('veicoli/form.html', 
                         form=form, 
                         titolo=f'Modifica Veicolo {veicolo.targa}',
                         veicolo=veicolo,
                         nucleo_corrente=veicolo.nucleo)

@veicoli_bp.route('/dettaglio/<int:id>')
@login_required
def dettaglio_veicolo(id):
    # Verifica accesso e ottieni veicolo
    veicolo = validate_veicolo_access(id)
    
    # Ottieni manutenzioni e scadenze (sempre filtrate per sicurezza)
    from app.models import Manutenzione, Scadenza
    
    manutenzioni_recenti = Manutenzione.query.filter(
        and_(
            Manutenzione.veicolo_id == veicolo.id,
            # Se non admin o admin con filtro, verifica nucleo
            Manutenzione.nucleo == veicolo.nucleo if should_filter_by_nucleo() else True
        )
    ).order_by(Manutenzione.data_intervento.desc()).limit(5).all()
    
    scadenze_prossime = Scadenza.query.filter(
        and_(
            Scadenza.veicolo_id == veicolo.id,
            # Se non admin o admin con filtro, verifica nucleo
            Scadenza.nucleo == veicolo.nucleo if should_filter_by_nucleo() else True
        )
    ).order_by(Scadenza.data_scadenza).limit(5).all()
    
    return render_template('veicoli/dettaglio.html', 
                         veicolo=veicolo,
                         manutenzioni_recenti=manutenzioni_recenti,
                         scadenze_prossime=scadenze_prossime)

@veicoli_bp.route('/elimina/<int:id>', methods=['POST'])
@login_required
def elimina_veicolo(id):
    # Verifica accesso e ottieni veicolo
    veicolo = validate_veicolo_access(id)
    
    try:
        targa = veicolo.targa
        nucleo = veicolo.nucleo
        
        # Verifica se ha manutenzioni o scadenze collegate
        if veicolo.manutenzioni or veicolo.scadenze:
            flash(f'Impossibile eliminare il veicolo {targa}: ha manutenzioni o scadenze collegate', 'error')
            return redirect(url_for('veicoli.dettaglio_veicolo', id=id))
        
        db.session.delete(veicolo)
        db.session.commit()
        
        flash(f'Veicolo {targa} eliminato con successo dal nucleo {nucleo}', 'success')
        return redirect(url_for('veicoli.index_veicoli'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
        return redirect(url_for('veicoli.dettaglio_veicolo', id=id))
