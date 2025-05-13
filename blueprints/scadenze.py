from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from models import Scadenza, Veicolo
from datetime import datetime

scadenze_bp = Blueprint('scadenze', __name__, template_folder='../templates')

@scadenze_bp.route('/scadenze')
def scadenze():
    scs = Scadenza.query.all()
    return render_template('scadenze.html', scadenze=scs)

@scadenze_bp.route('/scadenze/aggiungi', methods=['GET','POST'])
def aggiungi_scadenza():
    if request.method == 'POST':
        veicolo_id = request.form['veicolo_id']
        tipo = request.form['tipo']
        data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
        s = Scadenza(veicolo_id=veicolo_id, tipo=tipo, data=data)
        db.session.add(s)
        db.session.commit()
        return redirect(url_for('scadenze.scadenze'))
    veicoli = Veicolo.query.all()
    return render_template('aggiungi_scadenza.html', veicoli=veicoli)
