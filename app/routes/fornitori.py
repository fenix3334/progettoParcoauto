from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Fornitore
from app.forms import FornitoreForm
from app.extensions import db

fornitori_bp = Blueprint('fornitori', __name__)

def clean_field(value):
    """Helper per pulire i campi vuoti"""
    if value and value.strip():
        return value.strip()
    return None

@fornitori_bp.route('/')
def index_fornitori():
    # Filtro per nucleo se necessario
    nucleo_filter = request.args.get('nucleo')
    query = Fornitore.query
    
    if nucleo_filter:
        query = query.filter_by(nucleo=nucleo_filter)
    
    # Ordinamento per ragione sociale
    query = query.order_by(Fornitore.ragione_sociale)
    
    page = request.args.get('page', 1, type=int)
    fornitori = query.paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('fornitori/index.html', fornitori=fornitori)

@fornitori_bp.route('/aggiungi', methods=['GET', 'POST'])
def aggiungi_fornitore():
    form = FornitoreForm()
    if form.validate_on_submit():
        try:
            fornitore = Fornitore(
                # CAMPI BASE
                ragione_sociale=form.ragione_sociale.data,
                partita_iva=clean_field(form.partita_iva.data),
                codice_fiscale=clean_field(form.codice_fiscale.data),
                indirizzo=clean_field(form.indirizzo.data),
                citta=form.citta.data,
                cap=form.cap.data,
                provincia=clean_field(form.provincia.data),
                
                # TELEFONI MULTIPLI
                telefono=clean_field(form.telefono.data),
                telefono_2=clean_field(form.telefono_2.data),
                telefono_3=clean_field(form.telefono_3.data),
                
                # EMAIL MULTIPLE
                email=clean_field(form.email.data),
                email_2=clean_field(form.email_2.data),
                email_3=clean_field(form.email_3.data),
                
                referente=clean_field(form.referente.data),
                
                # SETTORI MULTIPLI
                settore=clean_field(form.settore.data),
                settore_2=clean_field(form.settore_2.data),
                settore_3=clean_field(form.settore_3.data),
                settore_personalizzato=clean_field(form.settore_personalizzato.data),
                
                nucleo=form.nucleo.data,
                note=clean_field(form.note.data),
                attivo=form.attivo.data
            )
            
            db.session.add(fornitore)
            db.session.commit()
            flash(f'Fornitore {fornitore.ragione_sociale} aggiunto con successo!', 'success')
            return redirect(url_for('fornitori.index_fornitori'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio: {str(e)}', 'error')
            
    return render_template('fornitori/form.html', form=form, titolo='Aggiungi Fornitore')

@fornitori_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_fornitore(id):
    fornitore = Fornitore.query.get_or_404(id)
    form = FornitoreForm(obj=fornitore)
    
    if form.validate_on_submit():
        try:
            # AGGIORNA CAMPI BASE
            fornitore.ragione_sociale = form.ragione_sociale.data
            fornitore.partita_iva = clean_field(form.partita_iva.data)
            fornitore.codice_fiscale = clean_field(form.codice_fiscale.data)
            fornitore.indirizzo = clean_field(form.indirizzo.data)
            fornitore.citta = form.citta.data
            fornitore.cap = form.cap.data
            fornitore.provincia = clean_field(form.provincia.data)
            
            # AGGIORNA TELEFONI MULTIPLI
            fornitore.telefono = clean_field(form.telefono.data)
            fornitore.telefono_2 = clean_field(form.telefono_2.data)
            fornitore.telefono_3 = clean_field(form.telefono_3.data)
            
            # AGGIORNA EMAIL MULTIPLE
            fornitore.email = clean_field(form.email.data)
            fornitore.email_2 = clean_field(form.email_2.data)
            fornitore.email_3 = clean_field(form.email_3.data)
            
            fornitore.referente = clean_field(form.referente.data)
            
            # AGGIORNA SETTORI MULTIPLI
            fornitore.settore = clean_field(form.settore.data)
            fornitore.settore_2 = clean_field(form.settore_2.data)
            fornitore.settore_3 = clean_field(form.settore_3.data)
            fornitore.settore_personalizzato = clean_field(form.settore_personalizzato.data)
            
            fornitore.nucleo = form.nucleo.data
            fornitore.note = clean_field(form.note.data)
            fornitore.attivo = form.attivo.data
            
            db.session.commit()
            flash(f'Fornitore {fornitore.ragione_sociale} modificato con successo!', 'success')
            return redirect(url_for('fornitori.index_fornitori'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante la modifica: {str(e)}', 'error')
            
    return render_template('fornitori/form.html', form=form, titolo='Modifica Fornitore')

@fornitori_bp.route('/dettagli/<int:id>')
def dettagli_fornitore(id):
    fornitore = Fornitore.query.get_or_404(id)
    return render_template('fornitori/dettagli.html', fornitore=fornitore)

@fornitori_bp.route('/elimina/<int:id>')
def elimina_fornitore(id):
    fornitore = Fornitore.query.get_or_404(id)
    
    try:
        # Controlla se ci sono manutenzioni associate
        if fornitore.manutenzioni:
            flash(f'Impossibile eliminare {fornitore.ragione_sociale}: ci sono {len(fornitore.manutenzioni)} manutenzioni associate a questo fornitore.', 'error')
            return redirect(url_for('fornitori.index_fornitori'))
        
        # Controlla se ci sono veicoli noleggio associati
        if fornitore.veicoli_noleggio:
            flash(f'Impossibile eliminare {fornitore.ragione_sociale}: ci sono {len(fornitore.veicoli_noleggio)} veicoli noleggio associati a questo fornitore.', 'error')
            return redirect(url_for('fornitori.index_fornitori'))
        
        ragione_sociale = fornitore.ragione_sociale  # Salva il nome prima di eliminare
        db.session.delete(fornitore)
        db.session.commit()
        flash(f'Fornitore {ragione_sociale} eliminato con successo!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione: {str(e)}', 'error')
        
    return redirect(url_for('fornitori.index_fornitori'))
