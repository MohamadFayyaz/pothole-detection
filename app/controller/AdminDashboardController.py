from app import app, db
from flask import request, render_template, redirect, url_for, session, flash, jsonify
from app.model.PotholeReportModel import PotholeReportModel
from collections import Counter
from datetime import datetime
from sqlalchemy import extract, func, or_
from config import Config

import os
import json

def dashboard():
    reportsCoordinate = db.session.query(
        PotholeReportModel.pothole_report_id,
        PotholeReportModel.latitude,
        PotholeReportModel.longtitude,
        PotholeReportModel.address,
        PotholeReportModel.image
    ).filter_by(status='proses').order_by(PotholeReportModel.user_id.desc()).all()
    reports_data = [
    {
        'pothole_report_id': report.pothole_report_id,
        'latitude': float(report.latitude),
        'longtitude': float(report.longtitude),
        'address': report.address,
        'image': report.image,
    }
    for report in reportsCoordinate
    ]
    reports_json = json.dumps(reports_data)

    # ambil awal bulan dan akhir bulan sekarang
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    start_of_next_month = datetime(now.year + 1, 1, 1) if now.month == 12 else datetime(now.year, now.month + 1, 1)

    status_counts = PotholeReportModel.query.with_entities(
        PotholeReportModel.status,
        func.count(PotholeReportModel.pothole_report_id)
    ).filter(
        PotholeReportModel.datetime >= start_of_month,
        PotholeReportModel.datetime < start_of_next_month
    ).group_by(
        PotholeReportModel.status
    ).all()

    statuses = ['proses', 'ditolak', 'selesai']
    result = {status: 0 for status in statuses}
    result.update({status: count for status, count in status_counts})

    
    return render_template('admin/dashboard.html',reports_json=reports_json,report_status=result)

def chart():
    data = PotholeReportModel.query.with_entities(PotholeReportModel.kecamatan).filter(
    or_(
        PotholeReportModel.status == 'proses',
        PotholeReportModel.status == 'selesai'
    )).all()

    # Ambil nama kecamatan dan simpan dalam list (pastikan sudah strip dan lower untuk konsistensi)
    kecamatan_list = [row.kecamatan.strip().lower() for row in data if row.kecamatan]

    # Hitung jumlah laporan per kecamatan
    count = Counter(kecamatan_list)

    return jsonify([
        {"kecamatan": k.title(), "jumlah_laporan": v}
        for k, v in count.items()
    ])

def get_yearly_reports():
    current_year = datetime.now().year
    reports = PotholeReportModel.query.filter(
    or_(
        PotholeReportModel.status == 'proses',
        PotholeReportModel.status == 'selesai'
    )).filter(extract('year', PotholeReportModel.datetime) == current_year).all()
    reports_data = {}
    for month in range(1, 13):
        reports_data[f"{current_year}-{month:02d}"] = 0

    for report in reports:
        report_month = report.datetime.strftime("%Y-%m")
        if report_month in reports_data:
            reports_data[report_month] += 1

    return reports_data

def yearly_reports():
    yearly_reports = get_yearly_reports()
    return jsonify(yearly_reports)


def update_report_dashboard_status(report_id):
    new_status = request.form.get('status')
    report = PotholeReportModel.query.filter_by(pothole_report_id=report_id).first()
    if not report:
        flash("Data tidak ditemukan!", "danger")
        return redirect(url_for('dashboard_admin'))
    report.status = new_status
    report.administrator_id = session['admin']['id']
    db.session.commit()
    return redirect(url_for('dashboard_admin'))

def report_dashboard_delete(report_id):
    report = PotholeReportModel.query.filter_by(pothole_report_id=report_id).first()
    if not report:
        flash("Data tidak ditemukan!", "danger")
        return redirect(url_for('dashboard_admin'))

    # Tentukan path file gambarnya
    os.remove(os.path.join(Config.REPORT_FOLDER, report.image))
    db.session.delete(report)
    db.session.commit()
    flash("Data berhasil dihapus!", "success")
    return redirect(url_for('dashboard_admin'))