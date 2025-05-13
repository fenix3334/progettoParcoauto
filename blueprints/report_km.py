from flask import Blueprint, render_template
from models import Veicolo, KmLog
from datetime import date
report_bp = Blueprint('report', __name__, template_folder='../templates')

@report_bp.route('/report_km')
def report_km():
    data = []
    for v in Veicolo.query.all():
        logs = sorted(v.logs, key=lambda l: l.data)
        from collections import defaultdict
        qdata = defaultdict(list)
        for l in logs:
            year, quarter = l.data.year, ((l.data.month-1)//3)+1
            qdata[(year, quarter)].append(l)
        for (year, quarter), lst in qdata.items():
            start, end = lst[0], lst[-1]
            data.append({
                'veicolo': v,
                'year': year,
                'quarter': quarter,
                'km_start': start.km,
                'km_end': end.km,
                'delta': end.km - start.km
            })
    return render_template('report_km.html', data=data)
