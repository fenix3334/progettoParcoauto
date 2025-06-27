from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Manutenzione
from app.forms import ManutenzioneForm
from app.extensions import db

manutenzioni_bp = Blueprint('manutenzioni', __name__)

@manutenzioni_bp.route('/')
def index_manutenzioni():
    page = request.args.get('page', 1, type=int)
    manutenzioni = Manutenzione.query.order_by(
        Manutenzione.data_intervento.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    return render_template('manutenzioni/index.html', manutenzioni=manutenzioni)

@manutenzioni_bp.route('/aggiungi', methods=['GET', 'POST'])
def aggiungi_manutenzione():
    form = ManutenzioneForm()
    if form.validate_on_submit():
        manutenzione = Manutenzione(
            veicolo_id=form.veicolo_id.data,
            fornitore_id=form.fornitore_id.data if form.fornitore_id.data else None,
            data_intervento=form.data_intervento.data,
            km_intervento=form.km_intervento.data,
            tipo_intervento=form.tipo_intervento.data,
            descrizione=form.descrizione.data,
            costo=form.costo.data,
            numero_fattura=form.numero_fattura.data,
            data_fattura=form.data_fattura.data,
            garanzia_mesi=form.garanzia_mesi.data,
            prossima_scadenza_km=form.prossima_scadenza_km.data,
            note=form.note.data
        )
        db.session.add(manutenzione)
        db.session.commit()
        flash('Manutenzione aggiunta con successo!', 'success')
        return redirect(url_for('manutenzioni.index_manutenzioni'))
    return render_template('manutenzioni/form.html', form=form, titolo='Aggiungi Manutenzione')

@manutenzioni_bp.route('/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_manutenzione(id):
    manutenzione = Manutenzione.query.get_or_404(id)
    form = ManutenzioneForm(obj=manutenzione)
    if form.validate_on_submit():
        form.populate_obj(manutenzione)
        db.session.commit()
        flash('Manutenzione modificata con successo!', 'success')
        return redirect(url_for('manutenzioni.index_manutenzioni'))
    return render_template('manutenzioni/form.html', form=form, titolo='Modifica Manutenzione')

@manutenzioni_bp.route('/elimina/<int:id>')
def elimina_manutenzione(id):
    manutenzione = Manutenzione.query.get_or_404(id)
    db.session.delete(manutenzione)
    db.session.commit()
    flash('Manutenzione eliminata con successo!', 'success')
    return redirect(url_for('manutenzioni.index_manutenzioni'))
