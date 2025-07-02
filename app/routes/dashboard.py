from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.models import Veicolo, Fornitore, Manutenzione, Scadenza
from app.extensions import db
from datetime import datetime, date
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    # Statistiche generali
    stats = {
        'totale_veicoli': Veicolo.query.count(),
        'veicoli_attivi': Veicolo.query.filter_by(stato='Attivo').count(),
        'totale_fornitori': Fornitore.query.count(),
        'fornitori_attivi': Fornitore.query.filter_by(attivo=True).count(),
        'totale_manutenzioni': Manutenzione.query.count(),
        'scadenze_urgenti': Scadenza.query.filter(
            Scadenza.data_scadenza <= func.date('now', '+30 days'),
            Scadenza.stato == 'Attiva'
        ).count()
    }
    
    # Scadenze urgenti
    scadenze_urgenti = Scadenza.query.filter(
        Scadenza.data_scadenza <= func.date('now', '+30 days'),
        Scadenza.stato == 'Attiva'
    ).order_by(Scadenza.data_scadenza).limit(5).all()
    
    # Ultime manutenzioni
    ultime_manutenzioni = Manutenzione.query.order_by(
        Manutenzione.data_intervento.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html', 
                         stats=stats,
                         scadenze_urgenti=scadenze_urgenti,
                         ultime_manutenzioni=ultime_manutenzioni)
