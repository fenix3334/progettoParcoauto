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
        veicolo = Veicolo(
            targa=form.targa.data,
            marca=form.marca.data,
            modello=form.modello.data,
            anno_immatricolazione=form.anno_immatricolazione.data,
            data_immatricolazione=form.data_immatricolazione.data,
            km_attuali=form.km_attuali.data,
            carburante=form.carburante.data,
            cilindrata=form.cilindrata.data,
            colore=form.colore.data,
            stato=form.stato.data,
            note=form.note.data
        )
        db.session.add(veicolo)
        db.session.commit()
        flash('Veicolo aggiunto con successo!', 'success')
        return redirect(url_for('veicoli.index_veicoli'))
    return render_template('veicoli/form.html', form=form, titolo='Aggiungi Veicolo')

@veicoli_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
@login_required
def modifica_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    form = VeicoloForm(obj=veicolo)
    if form.validate_on_submit():
        form.populate_obj(veicolo)
        db.session.commit()
        flash('Veicolo modificato con successo!', 'success')
        return redirect(url_for('veicoli.index_veicoli'))
    return render_template('veicoli/form.html', form=form, titolo='Modifica Veicolo')

@veicoli_bp.route('/elimina/<int:id>')
@login_required
def elimina_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    db.session.delete(veicolo)
    db.session.commit()
    flash('Veicolo eliminato con successo!', 'success')
    return redirect(url_for('veicoli.index_veicoli'))

@veicoli_bp.route('/dettaglio/<int:id>')
@login_required
def dettaglio_veicolo(id):
    veicolo = Veicolo.query.get_or_404(id)
    return render_template('veicoli/dettaglio.html', veicolo=veicolo)
