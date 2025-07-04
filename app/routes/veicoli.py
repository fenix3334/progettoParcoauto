from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import Veicolo
from app.forms import VeicoloForm
from app.extensions import db

veicoli_bp = Blueprint('veicoli', __name__)

@veicoli_bp.route('/')
@login_required
def index_veicoli():
    page = request.args.get('page', 1, type=int)
    veicoli = Veicolo.query.paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('veicoli/index.html', veicoli=veicoli)

@veicoli_bp.route('/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_veicolo():
    form = VeicoloForm()
    if form.validate_on_submit():
        try:
            veicolo = Veicolo(
                # CAMPI BASE
                targa=form.targa.data.upper(),  # Sempre maiuscolo
                marca=form.marca.data,
                modello=form.modello.data,
                anno_immatricolazione=form.anno_immatricolazione.data,
                data_immatricolazione=form.data_immatricolazione.data,
                km_attuali=form.km_attuali.data,
                carburante=form.carburante.data,
                
                # CARBURANTE PERSONALIZZATO
                carburante_personalizzato=form.carburante_personalizzato.data if form.carburante_personalizzato.data else None,
                
                cilindrata=form.cilindrata.data,
                colore=form.colore.data,
                stato=form.stato.data,
                
                # CARTA CARBURANTE
                carta_carburante=form.carta_carburante.data if form.carta_carburante.data else None,
                pin_carburante=form.pin_carburante.data if form.pin_carburante.data else None,
                
                # SOCIETÀ NOLEGGIO
                societa_noleggio_id=form.societa_noleggio_id.data if form.societa_noleggio_id.data else None,
                
                # NUCLEO
                nucleo=form.nucleo.data,
                
                note=form.note.data
            )
            
            db.session.add(veicolo)
            db.session.commit()
            flash(f'Veicolo {veicolo.targa} aggiunto con successo!', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
            
    return render_template('veicoli/form.html', form=form, titolo='Aggiungi Veicolo')

@veicoli_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    form = VeicoloForm(obj=veicolo)
    
    if form.validate_on_submit():
        try:
            # AGGIORNA TUTTI I CAMPI ESPLICITAMENTE
            veicolo.targa = form.targa.data.upper()
            veicolo.marca = form.marca.data
            veicolo.modello = form.modello.data
            veicolo.anno_immatricolazione = form.anno_immatricolazione.data
            veicolo.data_immatricolazione = form.data_immatricolazione.data
            veicolo.km_attuali = form.km_attuali.data
            veicolo.carburante = form.carburante.data
            
            # CAMPI NUOVI CHE PRIMA MANCAVANO
            veicolo.carburante_personalizzato = form.carburante_personalizzato.data if form.carburante_personalizzato.data else None
            veicolo.carta_carburante = form.carta_carburante.data if form.carta_carburante.data else None
            veicolo.pin_carburante = form.pin_carburante.data if form.pin_carburante.data else None
            veicolo.societa_noleggio_id = form.societa_noleggio_id.data if form.societa_noleggio_id.data else None
            veicolo.nucleo = form.nucleo.data
            
            veicolo.cilindrata = form.cilindrata.data
            veicolo.colore = form.colore.data
            veicolo.stato = form.stato.data
            veicolo.note = form.note.data
            
            db.session.commit()
            flash(f'Veicolo {veicolo.targa} modificato con successo!', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
            
    return render_template('veicoli/form.html', form=form, titolo='Modifica Veicolo')

@veicoli_bp.route('/elimina/<int:id>')
@login_required
def elimina_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    db.session.delete(veicolo)
    db.session.commit()
    flash(f'Veicolo {veicolo.targa} eliminato con successo!', 'success')
    return redirect(url_for('veicoli.index_veicoli'))

@veicoli_bp.route('/dettaglio/<int:id>')
@login_required
def dettaglio_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    return render_template('veicoli/dettaglio.html', veicolo=veicolo)
