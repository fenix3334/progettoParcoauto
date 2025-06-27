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

@fornitori_bp.route('/aggiungi', methods=['GET', 'POST'])
def aggiungi_fornitore():
    form = FornitoreForm()
    if form.validate_on_submit():
        fornitore = Fornitore(
            ragione_sociale=form.ragione_sociale.data,
            partita_iva=form.partita_iva.data,
            codice_fiscale=form.codice_fiscale.data,
            indirizzo=form.indirizzo.data,
            citta=form.citta.data,
            cap=form.cap.data,
            provincia=form.provincia.data,
            telefono=form.telefono.data,
            email=form.email.data,
            referente=form.referente.data,
            settore=form.settore.data,
            note=form.note.data,
            attivo=form.attivo.data
        )
        db.session.add(fornitore)
        db.session.commit()
        flash('Fornitore aggiunto con successo!', 'success')
        return redirect(url_for('fornitori.index_fornitori'))
    return render_template('fornitori/form.html', form=form, titolo='Aggiungi Fornitore')

@fornitori_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_fornitore(id):
    fornitore = Fornitore.query.get_or_404(id)
    form = FornitoreForm(obj=fornitore)
    if form.validate_on_submit():
        form.populate_obj(fornitore)
        db.session.commit()
        flash('Fornitore modificato con successo!', 'success')
        return redirect(url_for('fornitori.index_fornitori'))
    return render_template('fornitori/form.html', form=form, titolo='Modifica Fornitore')

@fornitori_bp.route('/elimina/<int:id>')
def elimina_fornitore(id):
    fornitore = Fornitore.query.get_or_404(id)
    db.session.delete(fornitore)
    db.session.commit()
    flash('Fornitore eliminato con successo!', 'success')
    return redirect(url_for('fornitori.index_fornitori'))
