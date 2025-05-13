from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, send_file
from io import BytesIO
import pandas as pd
from fpdf import FPDF
from app import db
from models import Veicolo
from models import KmLog

vehicoli_bp = Blueprint('vehicoli', __name__, template_folder='../templates')

@vehicoli_bp.route('/')
def home():
    veicoli = Veicolo.query.all()
    return render_template('home.html', veicoli=veicoli)

@vehicoli_bp.route('/aggiungi', methods=['GET','POST'])
def aggiungi():
    if request.method == 'POST':
        targa = request.form['targa']
        marca = request.form['marca']
        modello = request.form['modello']
        anno = request.form['anno'] or None
        km = request.form['km'] or None
        v = Veicolo(targa=targa, marca=marca, modello=modello, anno=anno, km=km)
        db.session.add(v)
        db.session.commit()

        # record initial km log
        km_date_str = request.form.get('km_date')
        if km_date_str:
            log_date = datetime.strptime(km_date_str, '%Y-%m-%d').date()
            km_log = KmLog(veicolo_id=v.id, km=v.km or 0, data=log_date)
            db.session.add(km_log)
            db.session.commit()
        return redirect(url_for('vehicoli.home'))
    return render_template('aggiungi.html')

@vehicoli_bp.route('/modifica/<int:id>', methods=['GET','POST'])
def modifica(id):
    veicolo = Veicolo.query.get_or_404(id)
    if request.method == 'POST':
        veicolo.targa = request.form['targa']
        veicolo.marca = request.form['marca']
        veicolo.modello = request.form['modello']
        veicolo.anno = request.form['anno'] or None
        veicolo.km = request.form['km'] or None
        db.session.commit()
        return redirect(url_for('vehicoli.home'))
    return render_template('modifica.html', veicolo=veicolo)

@vehicoli_bp.route('/dettaglio/<int:id>')
def dettaglio(id):
    veicolo = Veicolo.query.get_or_404(id)
    return render_template('dettaglio.html', veicolo=veicolo)

@vehicoli_bp.route('/export_excel')
def export_excel():
    veicoli = Veicolo.query.all()
    data = [{'Targa': v.targa, 'Marca': v.marca, 'Modello': v.modello, 'Anno': v.anno, 'KM': v.km} for v in veicoli]
    df = pd.DataFrame(data)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Veicoli')
    buf.seek(0)
    return send_file(buf, download_name='veicoli.xlsx', as_attachment=True)

@vehicoli_bp.route('/export_pdf')
def export_pdf():
    veicoli = Veicolo.query.all()
    buf = BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial','B',12)
    th = pdf.font_size * 1.5
    for h in ['Targa','Marca','Modello','Anno','KM']:
        pdf.cell(38, th, h, border=1)
    pdf.ln(th)
    pdf.set_font('Arial','',12)
    for v in veicoli:
        pdf.cell(38, th, v.targa, border=1)
        pdf.cell(38, th, v.marca, border=1)
        pdf.cell(38, th, v.modello, border=1)
        pdf.cell(38, th, str(v.anno), border=1)
        pdf.cell(38, th, str(v.km), border=1)
        pdf.ln(th)
    pdf.output(buf)
    buf.seek(0)
    return send_file(buf, download_name='veicoli.pdf', as_attachment=True)
