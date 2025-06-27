from flask import Blueprint, render_template, jsonify
from app.models import Veicolo, Fornitore, Manutenzione, Scadenza
from app.extensions import db
from datetime import datetime, date
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
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
    
    # KM totali e media
    km_stats = db.session.query(
        func.sum(Veicolo.km_attuali).label('km_totali'),
        func.avg(Veicolo.km_attuali).label('km_media')
    ).filter_by(stato='Attivo').first()
    
    stats['km_totali'] = int(km_stats.km_totali or 0)
    stats['km_media'] = int(km_stats.km_media or 0)
    
    # Scadenze urgenti
    scadenze_urgenti = Scadenza.query.filter(
        Scadenza.data_scadenza <= func.date('now', '+30 days'),
        Scadenza.stato == 'Attiva'
    ).order_by(Scadenza.data_scadenza).limit(5).all()
    
    # Ultime manutenzioni
    ultime_manutenzioni = Manutenzione.query.order_by(
        Manutenzione.data_intervento.desc()
    ).limit(5).all()
    
    # Costi mensili
    costi_mese = db.session.query(
        func.sum(Manutenzione.costo).label('totale')
    ).filter(
        func.strftime('%Y-%m', Manutenzione.data_intervento) == 
        datetime.now().strftime('%Y-%m')
    ).first()
    
    stats['costi_mese'] = float(costi_mese.totale or 0)
    
    return render_template('dashboard.html', 
                         stats=stats,
                         scadenze_urgenti=scadenze_urgenti,
                         ultime_manutenzioni=ultime_manutenzioni)

@dashboard_bp.route('/api/chart-data')
def chart_data():
    # Dati per grafici
    
    # Distribuzione carburante
    carburante_data = db.session.query(
        Veicolo.carburante,
        func.count(Veicolo.id).label('count')
    ).filter_by(stato='Attivo').group_by(Veicolo.carburante).all()
    
    # Manutenzioni per mese (ultimi 6 mesi)
    manutenzioni_mese = db.session.query(
        func.strftime('%Y-%m', Manutenzione.data_intervento).label('mese'),
        func.count(Manutenzione.id).label('count'),
        func.sum(Manutenzione.costo).label('costo_totale')
    ).filter(
        Manutenzione.data_intervento >= func.date('now', '-6 months')
    ).group_by(func.strftime('%Y-%m', Manutenzione.data_intervento)).all()
    
    return jsonify({
        'carburante': [{'label': item.carburante, 'value': item.count} 
                      for item in carburante_data],
        'manutenzioni': [{'mese': item.mese, 'count': item.count, 
                         'costo': float(item.costo_totale or 0)} 
                        for item in manutenzioni_mese]
    })
