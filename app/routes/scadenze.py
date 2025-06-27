from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Scadenza
from app.forms import ScadenzaForm
from app.extensions import db
from datetime import date

scadenze_bp = Blueprint('scadenze', __name__)

@scadenze_bp.route('/')
def index_scadenze():
    page = request.args.get('page', 1, type=int)
    filtro = request.args.get('filtro', 'tutte')
    
    query = Scadenza.query
    
    if filtro == 'urgenti':
        query = query.filter(Scadenza.data_scadenza <= date.today())
    elif filtro == 'attive':
        query = query.filter_by(stato='Attiva')
    
    scadenze = query.order_by(Scadenza.data_scadenza).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('scadenze/index.html', scadenze=scadenze, filtro=filtro)

@scadenze_bp.route('/aggiungi', methods=['GET', 'POST'])
def aggiungi_scadenza():
    form = ScadenzaForm()
    if form.validate_on_submit():
        scadenza = Scadenza(
            veicolo_id=form.veicolo_id.data,
            tipo_scadenza=form.tipo_scadenza.data,
            data_scadenza=form.data_scadenza.data,
            costo=form.costo.data,
            stato=form.stato.data,
            notifica_giorni=form.notifica_giorni.data,
            note=form.note.data
        )
        db.session.add(scadenza)
        db.session.commit()
        flash('Scadenza aggiunta con successo!', 'success')
        return redirect(url_for('scadenze.index_scadenze'))
    return render_template('scadenze/form.html', form=form, titolo='Aggiungi Scadenza')

@scadenze_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_scadenza(id):
    scadenza = Scadenza.query.get_or_404(id)
    form = ScadenzaForm(obj=scadenza)
    if form.validate_on_submit():
        form.populate_obj(scadenza)
        db.session.commit()
        flash('Scadenza modificata con successo!', 'success')
        return redirect(url_for('scadenze.index_scadenze'))
    return render_template('scadenze/form.html', form=form, titolo='Modifica Scadenza')

@scadenze_bp.route('/elimina/<int:id>')
def elimina_scadenza(id):
    scadenza = Scadenza.query.get_or_404(id)
    db.session.delete(scadenza)
    db.session.commit()
    flash('Scadenza eliminata con successo!', 'success')
    return redirect(url_for('scadenze.index_scadenze'))
