from flask import request, render_template, session, flash, redirect, url_for
from app import db, app
from app.model.PotholeReportModel import PotholeReportModel
from app.model.UserModel import UserModel
from app.model.AdministratorModel import AdministratorModel
from config import Config
import os
import json

def report():
    status_filter = request.args.get('status')
    if status_filter:
        reports = db.session.query(
            PotholeReportModel.pothole_report_id,
            PotholeReportModel.image,
            PotholeReportModel.address,
            PotholeReportModel.status,
            PotholeReportModel.longtitude,
            PotholeReportModel.latitude,
            PotholeReportModel.address,
            PotholeReportModel.datetime,
            UserModel.name.label("nama_user"),
            AdministratorModel.name.label("nama_admin")
        ).join(UserModel, PotholeReportModel.user_id == UserModel.user_id) \
        .outerjoin(AdministratorModel, PotholeReportModel.administrator_id == AdministratorModel.administrator_id) \
        .filter(PotholeReportModel.status == status_filter) \
        .order_by(PotholeReportModel.datetime.desc()) \
        .all()
    else:
        reports = db.session.query(
            PotholeReportModel.pothole_report_id,
            PotholeReportModel.image,
            PotholeReportModel.address,
            PotholeReportModel.status,
            PotholeReportModel.longtitude,
            PotholeReportModel.latitude,
            PotholeReportModel.address,
            PotholeReportModel.datetime,
            UserModel.name.label("nama_user"),
            AdministratorModel.name.label("nama_admin")
        ).join(UserModel, PotholeReportModel.user_id == UserModel.user_id) \
        .outerjoin(AdministratorModel, PotholeReportModel.administrator_id == AdministratorModel.administrator_id) \
        .order_by(PotholeReportModel.datetime.desc()) \
        .all()
    return render_template('admin/laporan.html',reports=reports)


def report_edit_admin(report_id):
    report = db.session.query(
        PotholeReportModel.pothole_report_id,
        PotholeReportModel.image,
        PotholeReportModel.address,
        PotholeReportModel.status,
        PotholeReportModel.longtitude,
        PotholeReportModel.latitude,
        PotholeReportModel.kecamatan,
        PotholeReportModel.datetime,
        PotholeReportModel.pesan,
        UserModel.name.label("nama_user"),
        UserModel.no_wa,
        PotholeReportModel.number_potholes,
        UserModel.username,
        AdministratorModel.name.label("nama_admin")
    ).join(UserModel, PotholeReportModel.user_id == UserModel.user_id) \
    .outerjoin(AdministratorModel, PotholeReportModel.administrator_id == AdministratorModel.administrator_id) \
    .order_by(PotholeReportModel.datetime.desc()) \
    .filter(PotholeReportModel.pothole_report_id == report_id) \
    .first()
    if not report:
        flash("Data tidak ditemukan!", "danger")
        return redirect(url_for('report_admin'))
    report_data = {
        'pothole_report_id': report.pothole_report_id,
        'latitude': float(report.latitude),
        'longtitude': float(report.longtitude),
    }
    report_json = json.dumps(report_data)
    return render_template('admin/laporan_edit.html',report=report,report_json=report_json)


def report_edit_proses():
    report_id = request.form['report_id']
    pesan = request.form['pesan']
    new_status = request.form['status']
    report = PotholeReportModel.query.filter_by(pothole_report_id=report_id).first()
    if not report:
        flash("Data tidak ditemukan!", "danger")
        return redirect(url_for('report_admin'))
    report.status = new_status
    report.pesan = pesan
    report.administrator_id = session['admin']['id']
    db.session.commit()
    return redirect(url_for('report_admin'))

def update_report_status(report_id):
    new_status = request.form.get('status')
    report = PotholeReportModel.query.filter_by(pothole_report_id=report_id).first()
    if not report:
        flash("Data tidak ditemukan!", "danger")
        return redirect(url_for('report_admin'))
    report.status = new_status
    report.administrator_id = session['admin']['id']
    db.session.commit()
    return redirect(url_for('report_admin'))

def report_delete(report_id):
    report = PotholeReportModel.query.filter_by(pothole_report_id=report_id).first()
    if not report:
        flash("Data tidak ditemukan!", "danger")
        return redirect(url_for('report_admin'))

    # Tentukan path file gambarnya
    os.remove(os.path.join(Config.REPORT_FOLDER, report.image))
    db.session.delete(report)
    db.session.commit()
    flash("Data berhasil dihapus!", "success")
    return redirect(url_for('report_admin'))