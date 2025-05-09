from flask import request, render_template, session
from app.model.PotholeReportModel import PotholeReportModel
from datetime import datetime
from sqlalchemy import func

def page():
    return render_template('index.html')
def dashboard():
    reports = PotholeReportModel.query.filter_by(user_id=session['user']['id'],).order_by(PotholeReportModel.user_id.desc()).limit(5)

    # ambil awal bulan dan akhir bulan sekarang
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    start_of_next_month = datetime(now.year + 1, 1, 1) if now.month == 12 else datetime(now.year, now.month + 1, 1)

    status_counts = PotholeReportModel.query.with_entities(
        PotholeReportModel.status,
        func.count(PotholeReportModel.pothole_report_id)
    ).filter(
        PotholeReportModel.user_id == session['user']['id'],
        PotholeReportModel.datetime >= start_of_month,
        PotholeReportModel.datetime < start_of_next_month
    ).group_by(
        PotholeReportModel.status
    ).all()

    statuses = ['proses', 'ditolak', 'selesai']
    result = {status: 0 for status in statuses}
    result.update({status: count for status, count in status_counts})

    total_reports=sum(result.values())
    
    return render_template('user/dashboard.html',reports=reports,report_status=result,total_reports=total_reports)
def login():
    return render_template('user/login.html')