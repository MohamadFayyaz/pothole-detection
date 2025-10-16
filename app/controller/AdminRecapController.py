from app import app, db
import os
from flask import request, render_template, make_response,session,jsonify
from app.model.PotholeReportModel import PotholeReportModel
from app.model.UserModel import UserModel
from collections import Counter
from datetime import datetime
from sqlalchemy import extract, func, or_
from calendar import monthrange

import json
import pdfkit

def recap():
    current_year = datetime.now().year
    years = []

    for y in range(2000, current_year + 26):  # +26 karena range akhir tidak inklusif
        years.append({
            'value': y,
            'selected': y == current_year
        })
    return render_template('admin/recap.html', years=years)

def preview():
    mode = request.form.get('mode')
    if mode == 'perbulan':
        bulan = int(request.form.get('bulan'))
        tahun = int(request.form.get('tahun'))
        time = {
        'bulan': bulan,
        'tahun': tahun,
        }
        
        reportsCoordinate = db.session.query(
            PotholeReportModel.pothole_report_id,
            PotholeReportModel.latitude,
            PotholeReportModel.longtitude,
            PotholeReportModel.address,
            PotholeReportModel.image
        ).filter(
            db.extract('month', PotholeReportModel.datetime) == bulan,
            db.extract('year', PotholeReportModel.datetime) == tahun
        ) \
        .filter_by(status='proses').order_by(PotholeReportModel.user_id.desc()).all()
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

        # ambil 5 data
        reports_table = db.session.query(
            PotholeReportModel.pothole_report_id,
            PotholeReportModel.address,
            PotholeReportModel.status,
            PotholeReportModel.datetime,
            PotholeReportModel.address,
            PotholeReportModel.image,
            UserModel.name.label("nama_user")
        ).join(UserModel, PotholeReportModel.user_id == UserModel.user_id) \
        .filter(
            db.extract('month', PotholeReportModel.datetime) == bulan,
            db.extract('year', PotholeReportModel.datetime) == tahun
        )\
        .filter(PotholeReportModel.status == 'proses').order_by(PotholeReportModel.user_id.desc()).all()
        # Perbaikan: tanggal awal dan akhir berdasarkan bulan/tahun yang dipilih
        start_of_month = datetime(tahun, bulan, 1)
        if bulan == 12:
            start_of_next_month = datetime(tahun + 1, 1, 1)
        else:
            start_of_next_month = datetime(tahun, bulan + 1, 1)

        status_counts = PotholeReportModel.query.with_entities(
            PotholeReportModel.status,
            func.count(PotholeReportModel.pothole_report_id)
        ).filter(
            db.extract('month', PotholeReportModel.datetime) == bulan,
            db.extract('year', PotholeReportModel.datetime) == tahun
        ).group_by(PotholeReportModel.status).all()

        statuses = ['proses', 'ditolak', 'selesai']
        result = {status: 0 for status in statuses}
        result.update({status: count for status, count in status_counts})
        return render_template('admin/recap_preview_bulan.html',reports_json=reports_json,report_status=result,reports_table=reports_table,month=bulan,year=tahun)
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
        
        reportsCoordinate = db.session.query(
            PotholeReportModel.pothole_report_id,
            PotholeReportModel.latitude,
            PotholeReportModel.longtitude,
            PotholeReportModel.address,
            PotholeReportModel.image
        ).filter(PotholeReportModel.datetime.between(mulai, akhir)) \
        .filter_by(status='proses').order_by(PotholeReportModel.user_id.desc()).all()
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

        reports_table = db.session.query(
            PotholeReportModel.pothole_report_id,
            PotholeReportModel.address,
            PotholeReportModel.status,
            PotholeReportModel.datetime,
            PotholeReportModel.address,
            PotholeReportModel.image,
            UserModel.name.label("nama_user")
        ).join(UserModel, PotholeReportModel.user_id == UserModel.user_id) \
        .filter(PotholeReportModel.datetime.between(mulai, akhir)) \
        .filter(PotholeReportModel.status == 'proses').order_by(PotholeReportModel.user_id.desc()).all()

        # ambil awal bulan dan akhir bulan sekarang
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        start_of_next_month = datetime(now.year + 1, 1, 1) if now.month == 12 else datetime(now.year, now.month + 1, 1)

        status_counts = PotholeReportModel.query.with_entities(
            PotholeReportModel.status,
            func.count(PotholeReportModel.pothole_report_id)
        ).filter(PotholeReportModel.datetime.between(mulai, akhir))\
        .group_by(
            PotholeReportModel.status
        ).all()

        statuses = ['proses', 'ditolak', 'selesai']
        result = {status: 0 for status in statuses}
        result.update({status: count for status, count in status_counts})
        return render_template('admin/recap_preview_tanggal.html',reports_json=reports_json,report_status=result,reports_table=reports_table)
    elif mode == 'pertahun':
        tahun = int(request.form.get('tahun'))
        time = {'tahun': tahun}

        start_of_year = datetime(tahun, 1, 1)
        end_of_year = datetime(tahun, 12, 31, 23, 59, 59)

        reportsCoordinate = db.session.query(
            PotholeReportModel.pothole_report_id,
            PotholeReportModel.latitude,
            PotholeReportModel.longtitude,
            PotholeReportModel.address,
            PotholeReportModel.image
        ).filter(
            PotholeReportModel.datetime.between(start_of_year, end_of_year),
            PotholeReportModel.status == 'proses'
        ).order_by(PotholeReportModel.user_id.desc()).all()

        reports_data = [{
            'pothole_report_id': report.pothole_report_id,
            'latitude': float(report.latitude),
            'longtitude': float(report.longtitude),
            'address': report.address,
            'image': report.image,
        } for report in reportsCoordinate]
        reports_json = json.dumps(reports_data)

        reports_table = db.session.query(
            PotholeReportModel.pothole_report_id,
            PotholeReportModel.address,
            PotholeReportModel.status,
            PotholeReportModel.datetime,
            PotholeReportModel.image,
            UserModel.name.label("nama_user")
        ).join(UserModel, PotholeReportModel.user_id == UserModel.user_id) \
        .filter(
            PotholeReportModel.datetime.between(start_of_year, end_of_year),
            PotholeReportModel.status == 'proses'
        ).order_by(PotholeReportModel.user_id.desc()).all()

        status_counts = PotholeReportModel.query.with_entities(
            PotholeReportModel.status,
            func.count(PotholeReportModel.pothole_report_id)
        ).filter(
            PotholeReportModel.datetime.between(start_of_year, end_of_year),
        ).group_by(PotholeReportModel.status).all()

        statuses = ['proses', 'ditolak', 'selesai']
        result = {status: 0 for status in statuses}
        result.update({status: count for status, count in status_counts})

        return render_template('admin/recap_preview_tahun.html', reports_json=reports_json, report_status=result, reports_table=reports_table)

def monthly_chart():
    data = request.get_json()
    year = int(data.get("year"))
    month = int(data.get("month"))
    data = PotholeReportModel.query.with_entities(PotholeReportModel.kecamatan).filter(
    or_(
        PotholeReportModel.status == 'proses',
        PotholeReportModel.status == 'selesai'
    ),
        extract('year', PotholeReportModel.datetime) == year,
        extract('month', PotholeReportModel.datetime) == month
    ).all()

    # Ambil nama kecamatan dan simpan dalam list (pastikan sudah strip dan lower untuk konsistensi)
    kecamatan_list = [row.kecamatan.strip().lower() for row in data if row.kecamatan]

    # Hitung jumlah laporan per kecamatan
    count = Counter(kecamatan_list)

    return jsonify([
        {"kecamatan": k.title(), "jumlah_laporan": v}
        for k, v in count.items()
    ])


def get_monthly_reports(year: int, month: int):
    # Dapatkan jumlah hari dalam bulan dan tahun tersebut
    _, last_day = monthrange(year, month)

    reports = PotholeReportModel.query.filter(
        or_(
            PotholeReportModel.status == 'proses',
            PotholeReportModel.status == 'selesai'
        )
    ).filter(
        extract('year', PotholeReportModel.datetime) == year,
        extract('month', PotholeReportModel.datetime) == month
    ).all()

    reports_data = {f"{day:02d}": 0 for day in range(1, last_day + 1)}

    for report in reports:
        day = report.datetime.strftime("%d")
        if day in reports_data:
            reports_data[day] += 1

    return reports_data

def recap_process():
    mode = request.form.get('mode')
    action = request.form.get('action', 'preview')
    reports = []
    time = {}

    # Ambil data sesuai mode
    if mode == 'perbulan':
        bulan = int(request.form.get('bulan'))
        tahun = int(request.form.get('tahun'))
        time = {'bulan': bulan, 'tahun': tahun}
        reports = PotholeReportModel.query.filter(
            db.extract('month', PotholeReportModel.datetime) == bulan,
            db.extract('year', PotholeReportModel.datetime) == tahun
        ).all()

        status_counts = PotholeReportModel.query.with_entities(
            PotholeReportModel.status,
            func.count(PotholeReportModel.pothole_report_id)
        ).filter(
            db.extract('month', PotholeReportModel.datetime) == bulan,
            db.extract('year', PotholeReportModel.datetime) == tahun
        ).group_by(PotholeReportModel.status).all()

        statuses = ['proses', 'ditolak', 'selesai']
        result = {status: 0 for status in statuses}
        result.update({status: count for status, count in status_counts})
    elif mode == 'pertahun':
        tahun = int(request.form.get('tahun'))
        time = {'tahun': tahun}

        start_of_year = datetime(tahun, 1, 1)
        end_of_year = datetime(tahun, 12, 31, 23, 59, 59)

        reports = PotholeReportModel.query.filter(
            PotholeReportModel.datetime.between(start_of_year, end_of_year),
        ).all()

        status_counts = PotholeReportModel.query.with_entities(
            PotholeReportModel.status,
            func.count(PotholeReportModel.pothole_report_id)
        ).filter(
            PotholeReportModel.datetime.between(start_of_year, end_of_year),
        ).group_by(PotholeReportModel.status).all()

        statuses = ['proses', 'ditolak', 'selesai']
        result = {status: 0 for status in statuses}
        result.update({status: count for status, count in status_counts})

    elif mode == 'pertanggal':
        tgl_mulai = request.form.get('tanggal_mulai')
        tgl_akhir = request.form.get('tanggal_akhir')
        mulai = datetime.strptime(tgl_mulai, '%Y-%m-%d')
        akhir = datetime.strptime(tgl_akhir, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        time = {'tgl_mulai': tgl_mulai, 'tgl_akhir': tgl_akhir}
        reports = PotholeReportModel.query.filter(
            PotholeReportModel.datetime.between(mulai, akhir)
        ).all()
        
        status_counts = PotholeReportModel.query.with_entities(
            PotholeReportModel.status,
            func.count(PotholeReportModel.pothole_report_id)
        ).filter(
            PotholeReportModel.datetime.between(mulai, akhir)
        ).group_by(PotholeReportModel.status).all()

        statuses = ['proses', 'ditolak', 'selesai']
        result = {status: 0 for status in statuses}
        result.update({status: count for status, count in status_counts})

    # Render HTML template sebagai string
    html = render_template(
        'admin/print_recap.html',
        time=time,
        reports=reports,
        mode=mode,
        report_status=result,
        now=datetime.now)

    if action == 'download':
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

        # Convert ke PDF langsung dari HTML string
        pdf = pdfkit.from_string(html, False, configuration=config, options={
            'enable-local-file-access': None
        })

        # Kirim sebagai file download
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=rekap_laporan.pdf'
        return response

    else:
        return html
