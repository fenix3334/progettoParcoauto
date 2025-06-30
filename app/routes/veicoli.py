from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Veicolo, Fornitore
from app.forms import VeicoloForm
from app.extensions import db

veicoli_bp = Blueprint('veicoli', __name__)

def clean_field(value):
    """Helper per pulire i campi vuoti"""
    if value and value.strip():
        return value.strip()
    return None

@veicoli_bp.route('/')
def index_veicoli():
    # Filtro per nucleo se necessario
    nucleo_filter = request.args.get('nucleo')
    query = Veicolo.query
    
    if nucleo_filter:
        query = query.filter_by(nucleo=nucleo_filter)
    
    # Ordinamento per targa
    query = query.order_by(Veicolo.targa)
    
    page = request.args.get('page', 1, type=int)
    veicoli = query.paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('veicoli/index.html', veicoli=veicoli)

@veicoli_bp.route('/aggiungi', methods=['GET', 'POST'])
def aggiungi_veicolo():
    form = VeicoloForm()
    if form.validate_on_submit():
        try:
            # Determina il carburante finale
            carburante_finale = form.carburante.data
            carburante_personalizzato = None
            
            if form.carburante.data == 'Personalizzato':
                carburante_personalizzato = clean_field(form.carburante_personalizzato.data)
                if not carburante_personalizzato:
                    flash('Quando selezioni "Personalizzato" devi specificare il tipo di carburante.', 'error')
                    return render_template('veicoli/form.html', form=form, titolo='Aggiungi Veicolo')
            
            veicolo = Veicolo(
                # CAMPI BASE
                targa=form.targa.data.upper(),  # Targa sempre maiuscola
                marca=form.marca.data,
                modello=form.modello.data,
                anno_immatricolazione=form.anno_immatricolazione.data,
                data_immatricolazione=form.data_immatricolazione.data,
                km_attuali=form.km_attuali.data or 0,
                
                # CARBURANTE
                carburante=carburante_finale,
                carburante_personalizzato=carburante_personalizzato,
                
                cilindrata=form.cilindrata.data,
                colore=clean_field(form.colore.data),
                stato=form.stato.data,
                
                # CARTA CARBURANTE
                carta_carburante=clean_field(form.carta_carburante.data),
                pin_carburante=clean_field(form.pin_carburante.data),
                
                # SOCIETÀ NOLEGGIO
                societa_noleggio_id=form.societa_noleggio_id.data,
                
                # NUCLEO
                nucleo=form.nucleo.data,
                
                note=clean_field(form.note.data)
            )
            
            db.session.add(veicolo)
            db.session.commit()
            flash('Veicolo aggiunto con successo!', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
            
    return render_template('veicoli/form.html', form=form, titolo='Aggiungi Veicolo')

@veicoli_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    form = VeicoloForm(obj=veicolo)
    
    if form.validate_on_submit():
        try:
            # Determina il carburante finale
            carburante_finale = form.carburante.data
            carburante_personalizzato = veicolo.carburante_personalizzato  # Mantieni quello esistente
            
            if form.carburante.data == 'Personalizzato':
                carburante_personalizzato = clean_field(form.carburante_personalizzato.data)
                if not carburante_personalizzato:
                    flash('Quando selezioni "Personalizzato" devi specificare il tipo di carburante.', 'error')
                    return render_template('veicoli/form.html', form=form, titolo='Modifica Veicolo')
            elif form.carburante.data != 'Personalizzato':
                carburante_personalizzato = None  # Reset se non è più personalizzato
            
            # AGGIORNA CAMPI BASE
            veicolo.targa = form.targa.data.upper()
            veicolo.marca = form.marca.data
            veicolo.modello = form.modello.data
            veicolo.anno_immatricolazione = form.anno_immatricolazione.data
            veicolo.data_immatricolazione = form.data_immatricolazione.data
            veicolo.km_attuali = form.km_attuali.data or 0
            
            # AGGIORNA CARBURANTE
            veicolo.carburante = carburante_finale
            veicolo.carburante_personalizzato = carburante_personalizzato
            
            veicolo.cilindrata = form.cilindrata.data
            veicolo.colore = clean_field(form.colore.data)
            veicolo.stato = form.stato.data
            
            # AGGIORNA CARTA CARBURANTE
            veicolo.carta_carburante = clean_field(form.carta_carburante.data)
            veicolo.pin_carburante = clean_field(form.pin_carburante.data)
            
            # AGGIORNA SOCIETÀ NOLEGGIO
            veicolo.societa_noleggio_id = form.societa_noleggio_id.data
            
            # AGGIORNA NUCLEO
            veicolo.nucleo = form.nucleo.data
            
            veicolo.note = clean_field(form.note.data)
            
            db.session.commit()
            flash('Veicolo modificato con successo!', 'success')
            return redirect(url_for('veicoli.index_veicoli'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
            
    return render_template('veicoli/form.html', form=form, titolo='Modifica Veicolo')

@veicoli_bp.route('/dettaglio/<int:id>')
def dettaglio_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    return render_template('veicoli/dettaglio.html', veicolo=veicolo)

@veicoli_bp.route('/elimina/<int:id>')
def elimina_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    
    try:
        # Controlla se ci sono manutenzioni associate
        if veicolo.manutenzioni:
            flash(f'Impossibile eliminare: ci sono {len(veicolo.manutenzioni)} manutenzioni associate a questo veicolo.', 'error')
            return redirect(url_for('veicoli.index_veicoli'))
        
        # Controlla se ci sono scadenze associate
        if veicolo.scadenze:
            flash(f'Impossibile eliminare: ci sono {len(veicolo.scadenze)} scadenze associate a questo veicolo.', 'error')
            return redirect(url_for('veicoli.index_veicoli'))
        
        db.session.delete(veicolo)
        db.session.commit()
        flash('Veicolo eliminato con successo!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
        
    return redirect(url_for('veicoli.index_veicoli'))
