from flask import Blueprint, render_template
from app import db
from models import Veicolo, Scadenza
from datetime import date, timedelta

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')

@dashboard_bp.route('/dashboard')
def dashboard():
    total = Veicolo.query.count()
    soon = Scadenza.query.filter(
        Scadenza.data.between(date.today(), date.today() + timedelta(days=30))
    ).count()
    avg_km = db.session.query(db.func.avg(Veicolo.km)).scalar() or 0

    data = db.session.query(Veicolo.anno, db.func.count(Veicolo.id))              .group_by(Veicolo.anno).all()
    labels = [str(r[0]) for r in data]
    values = [r[1] for r in data]

    return render_template('dashboard.html',
        total=total, soon=soon, avg_km=round(avg_km,0),
        labels=labels, values=values
    )
