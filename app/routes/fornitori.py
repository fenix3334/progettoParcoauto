from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Fornitore
from app.forms import FornitoreForm
from app.extensions import db

fornitori_bp = Blueprint('fornitori', __name__)

@fornitori_bp.route('/')
def index_fornitori():
    page = request.args.get('page', 1, type=int)
    fornitori = Fornitore.query.paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('fornitori/index.html', fornitori=fornitori)

def clean_field(field_data):
    """Pulisce un campo e restituisce None se vuoto"""
    if not field_data:
        return None
    cleaned = field_data.strip()
    return cleaned if cleaned else None

@fornitori_bp.route('/aggiungi', methods=['GET', 'POST'])
def aggiungi_fornitore():
    form = FornitoreForm()
    if form.validate_on_submit():
        try:
            fornitore = Fornitore(
                ragione_sociale=form.ragione_sociale.data,
                partita_iva=clean_field(form.partita_iva.data),
                codice_fiscale=clean_field(form.codice_fiscale.data),
                indirizzo=clean_field(form.indirizzo.data),
                citta=form.citta.data,
                cap=form.cap.data,
                provincia=clean_field(form.provincia.data),
                telefono=clean_field(form.telefono.data),
                telefono_2=clean_field(form.telefono_2.data),
                telefono_3=clean_field(form.telefono_3.data),
                email=clean_field(form.email.data),
                email_2=clean_field(form.email_2.data),
                email_3=clean_field(form.email_3.data),
                referente=clean_field(form.referente.data),
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
            if "UNIQUE constraint failed: fornitori.partita_iva" in str(e):
                flash('Errore: Esiste già un fornitore con questa Partita IVA', 'error')
            else:
                flash(f'Errore nell\'aggiunta del fornitore: {str(e)}', 'error')
    
    return render_template('fornitori/form.html', form=form, titolo='Aggiungi Fornitore')

@fornitori_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_fornitore(id):
    fornitore = Fornitore.query.get_or_404(id)
    form = FornitoreForm(obj=fornitore)
    
    if form.validate_on_submit():
        try:
            # Aggiorna tutti i campi con controllo retrocompatibilità
            fornitore.ragione_sociale = form.ragione_sociale.data
            fornitore.partita_iva = clean_field(form.partita_iva.data)
            fornitore.codice_fiscale = clean_field(form.codice_fiscale.data)
            fornitore.indirizzo = clean_field(form.indirizzo.data)
            fornitore.citta = form.citta.data
            fornitore.cap = form.cap.data
            fornitore.provincia = clean_field(form.provincia.data)
            fornitore.telefono = clean_field(form.telefono.data)
            fornitore.email = clean_field(form.email.data)
            fornitore.referente = clean_field(form.referente.data)
            fornitore.settore = clean_field(form.settore.data)
            fornitore.note = clean_field(form.note.data)
            fornitore.attivo = form.attivo.data
            
            # Aggiorna i nuovi campi solo se esistono nella tabella
            if hasattr(fornitore, 'telefono_2'):
                fornitore.telefono_2 = clean_field(form.telefono_2.data)
            if hasattr(fornitore, 'telefono_3'):
                fornitore.telefono_3 = clean_field(form.telefono_3.data)
            if hasattr(fornitore, 'email_2'):
                fornitore.email_2 = clean_field(form.email_2.data)
            if hasattr(fornitore, 'email_3'):
                fornitore.email_3 = clean_field(form.email_3.data)
            if hasattr(fornitore, 'settore_2'):
                fornitore.settore_2 = clean_field(form.settore_2.data)
            if hasattr(fornitore, 'settore_3'):
                fornitore.settore_3 = clean_field(form.settore_3.data)
            if hasattr(fornitore, 'settore_personalizzato'):
                fornitore.settore_personalizzato = clean_field(form.settore_personalizzato.data)
            if hasattr(fornitore, 'nucleo'):
                fornitore.nucleo = form.nucleo.data
            
            db.session.commit()
            flash(f'Fornitore {fornitore.ragione_sociale} modificato con successo!', 'success')
            return redirect(url_for('fornitori.index_fornitori'))
            
        except Exception as e:
            db.session.rollback()
            if "UNIQUE constraint failed: fornitori.partita_iva" in str(e):
                flash('Errore: Esiste già un fornitore con questa Partita IVA', 'error')
            else:
                flash(f'Errore nella modifica del fornitore: {str(e)}', 'error')
    
    return render_template('fornitori/form.html', form=form, titolo='Modifica Fornitore')

@fornitori_bp.route('/elimina/<int:id>')
def elimina_fornitore(id):
    fornitore = Fornitore.query.get_or_404(id)
    ragione_sociale = fornitore.ragione_sociale
    
    try:
        db.session.delete(fornitore)
        db.session.commit()
        flash(f'Fornitore {ragione_sociale} eliminato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore nell\'eliminazione del fornitore: {str(e)}', 'error')
    
    return redirect(url_for('fornitori.index_fornitori'))
