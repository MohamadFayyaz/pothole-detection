from app import app, db
from flask import request, render_template, redirect, url_for, session, flash, jsonify
from app.model.PotholeReportModel import PotholeReportModel
from datetime import datetime

def recap():
    current_year = datetime.now().year
    years = []

    for y in range(2000, current_year + 26):  # +26 karena range akhir tidak inklusif
        years.append({
            'value': y,
            'selected': y == current_year
        })
    return render_template('admin/recap.html', years=years)

def recap_process():
    mode = request.form.get('mode')
    if mode == 'perbulan':
        bulan = int(request.form.get('bulan'))
        tahun = int(request.form.get('tahun'))
        time = {
        'bulan': bulan,
        'tahun': tahun,
        }
        reports = PotholeReportModel.query.filter(
            db.extract('month', PotholeReportModel.datetime) == bulan,
            db.extract('year', PotholeReportModel.datetime) == tahun
        ).all()
    elif mode == 'pertanggal':
        tgl_mulai = request.form.get('tanggal_mulai')
        tgl_akhir = request.form.get('tanggal_akhir')
        mulai = datetime.strptime(tgl_mulai, '%Y-%m-%d')
        akhir = datetime.strptime(tgl_akhir, '%Y-%m-%d')
        akhir = akhir.replace(hour=23, minute=59, second=59) 
        time = {
        'tgl_mulai': tgl_mulai,
        'tgl_akhir': tgl_akhir,
        }
        if tgl_mulai and tgl_akhir:
            reports = PotholeReportModel.query.filter(
                PotholeReportModel.datetime.between(mulai, akhir)
            ).all()
            
    return render_template('admin/print_recap.html', time=time, reports=reports, mode=mode, now=datetime.now)
