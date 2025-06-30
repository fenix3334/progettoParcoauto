from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Veicolo, Fornitore
from app.forms import VeicoloForm
from app.extensions import db

veicoli_bp = Blueprint('veicoli', __name__)

@veicoli_bp.route('/')
def index_veicoli():
    page = request.args.get('page', 1, type=int)
    veicoli = Veicolo.query.paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('veicoli/index.html', veicoli=veicoli)

@veicoli_bp.route('/aggiungi', methods=['GET', 'POST'])
def aggiungi_veicolo():
    form = VeicoloForm()
    
    if form.validate_on_submit():
        # Gestisce il carburante personalizzato
        carburante_finale = form.carburante.data
        carburante_personalizzato = None
        
        if form.carburante.data == 'Personalizzato':
            carburante_finale = 'Personalizzato'
            carburante_personalizzato = form.carburante_personalizzato.data
        
        # Gestisce la società di noleggio (può essere None)
        societa_noleggio_id = form.societa_noleggio_id.data
        if societa_noleggio_id == '':
            societa_noleggio_id = None
        
        veicolo = Veicolo(
            targa=form.targa.data,
            marca=form.marca.data,
            modello=form.modello.data,
            anno_immatricolazione=form.anno_immatricolazione.data,
            data_immatricolazione=form.data_immatricolazione.data,
            km_attuali=form.km_attuali.data,
            carburante=carburante_finale,
            carburante_personalizzato=carburante_personalizzato,
            cilindrata=form.cilindrata.data,
            colore=form.colore.data,
            stato=form.stato.data,
            carta_carburante=form.carta_carburante.data,
            pin_carburante=form.pin_carburante.data,
            societa_noleggio_id=societa_noleggio_id,
            nucleo=form.nucleo.data,
            note=form.note.data
        )
        
        try:
            db.session.add(veicolo)
            db.session.commit()
            flash(f'Veicolo {veicolo.targa} aggiunto con successo!', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore nell\'aggiunta del veicolo: {str(e)}', 'error')
    
    return render_template('veicoli/form.html', form=form, titolo='Aggiungi Veicolo')

@veicoli_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    form = VeicoloForm(obj=veicolo)
    
    if form.validate_on_submit():
        # Gestisce il carburante personalizzato
        carburante_finale = form.carburante.data
        carburante_personalizzato = None
        
        if form.carburante.data == 'Personalizzato':
            carburante_finale = 'Personalizzato'
            carburante_personalizzato = form.carburante_personalizzato.data
        
        # Gestisce la società di noleggio (può essere None)
        societa_noleggio_id = form.societa_noleggio_id.data
        if societa_noleggio_id == '':
            societa_noleggio_id = None
        
        # Aggiorna tutti i campi (con controllo sicurezza)
        veicolo.targa = form.targa.data
        veicolo.marca = form.marca.data
        veicolo.modello = form.modello.data
        veicolo.anno_immatricolazione = form.anno_immatricolazione.data
        veicolo.data_immatricolazione = form.data_immatricolazione.data
        veicolo.km_attuali = form.km_attuali.data
        veicolo.carburante = carburante_finale
        
        # Aggiorna i nuovi campi solo se esistono nella tabella
        if hasattr(veicolo, 'carburante_personalizzato'):
            veicolo.carburante_personalizzato = carburante_personalizzato
        if hasattr(veicolo, 'cilindrata'):
            veicolo.cilindrata = form.cilindrata.data
        if hasattr(veicolo, 'colore'):
            veicolo.colore = form.colore.data
        
        veicolo.stato = form.stato.data
        
        # Nuovi campi con controllo
        if hasattr(veicolo, 'carta_carburante'):
            veicolo.carta_carburante = form.carta_carburante.data
        if hasattr(veicolo, 'pin_carburante'):
            veicolo.pin_carburante = form.pin_carburante.data
        if hasattr(veicolo, 'societa_noleggio_id'):
            veicolo.societa_noleggio_id = societa_noleggio_id
        if hasattr(veicolo, 'nucleo'):
            veicolo.nucleo = form.nucleo.data
        if hasattr(veicolo, 'note'):
            veicolo.note = form.note.data
        
        try:
            db.session.commit()
            flash(f'Veicolo {veicolo.targa} modificato con successo!', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore nella modifica del veicolo: {str(e)}', 'error')
    
    # Pre-compila il form con i dati esistenti
    if request.method == 'GET':
        # Se ha carburante personalizzato, imposta il select su "Personalizzato"
        # Usa getattr per sicurezza con veicoli vecchi
        carburante_personalizzato = getattr(veicolo, 'carburante_personalizzato', None)
        if carburante_personalizzato:
            form.carburante.data = 'Personalizzato'
            form.carburante_personalizzato.data = carburante_personalizzato
        
        # Imposta la società di noleggio se presente
        societa_noleggio_id = getattr(veicolo, 'societa_noleggio_id', None)
        if societa_noleggio_id:
            form.societa_noleggio_id.data = str(societa_noleggio_id)
    
    return render_template('veicoli/form.html', form=form, titolo='Modifica Veicolo')

@veicoli_bp.route('/elimina/<int:id>')
def elimina_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    targa = veicolo.targa
    
    try:
        db.session.delete(veicolo)
        db.session.commit()
        flash(f'Veicolo {targa} eliminato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore nell\'eliminazione del veicolo: {str(e)}', 'error')
    
    return redirect(url_for('veicoli.index_veicoli'))

@veicoli_bp.route('/dettaglio/<int:id>')
def dettaglio_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    return render_template('veicoli/dettaglio.html', veicolo=veicolo)
