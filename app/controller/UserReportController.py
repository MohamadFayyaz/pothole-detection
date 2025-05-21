from flask import request, render_template, session, flash, redirect, url_for
from app import db, app
from ultralytics import YOLO
from app.model.PotholeReportModel import PotholeReportModel
from app.model.AdministratorModel import AdministratorModel
from datetime import datetime, timedelta    
from config import Config

import base64
import imghdr
import random
import os
import re
import cv2
import numpy as np
import io
import logging

def report():
    reports = db.session.query(
            PotholeReportModel.pothole_report_id,
            PotholeReportModel.image,
            PotholeReportModel.address,
            PotholeReportModel.status,
            PotholeReportModel.datetime,
            PotholeReportModel.pesan,
            AdministratorModel.name.label("nama_admin")
        ).outerjoin(AdministratorModel, PotholeReportModel.administrator_id == AdministratorModel.administrator_id) \
        .filter(PotholeReportModel.user_id ==session['user']['id']) \
        .order_by(PotholeReportModel.datetime.desc()) \
        .all()
    return render_template('user/laporan.html',reports=reports)

def add_report():
    return render_template('user/add_laporan.html')

def maps():
    return render_template('user/photo.html')

def add_report_process():
    longtitude = request.form['longtitude']
    latitude = request.form['latitude']
    address = request.form['address']
    kecamatan = request.form['kecamatan']

    # Load image
    captureImage = request.form['captureImage']
    if not captureImage:
        flash(f"Gagal! foto wajib dikirim", "danger")
        return redirect(url_for('add_report'))

    
    img_str = re.search(r'base64,(.*)', captureImage).group(1)
    img_data = base64.b64decode(img_str)
    # img_bytes = captureImage.read()
    npimg = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    # Load model
    model = app.yolo_model
    results = model(img, conf=0.5)
    status = 'ditolak'

    for r in results:
        boxes = r.boxes
        num_detections = len(boxes)
        print(f"Jumlah lubang yang terdeteksi: {num_detections}")

        # Gambar hasil deteksi
        im_array = r.plot()
        resized_result = cv2.resize(im_array, (800, 600))

        # Simpan ke folder
        if not os.path.exists(Config.REPORT_FOLDER):
            os.makedirs(Config.REPORT_FOLDER)  # Membuat folder jika belum ada
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pothole_{timestamp}.jpg"
        file_path = os.path.join(Config.REPORT_FOLDER, filename)
        cv2.imwrite(file_path, resized_result)
    if num_detections > 0:
        status = 'proses'
    PotholeReport = PotholeReportModel(
        user_id=session['user']['id'],
        datetime=datetime.now(),
        latitude=latitude,
        longtitude=longtitude,
        image=filename,
        status=status,
        number_potholes=num_detections,
        address=address,
        kecamatan=kecamatan)

    db.session.add(PotholeReport)
    db.session.commit()
    if num_detections == 0:
        flash(f"Gagal! terdeteki {num_detections} jalan berlubang", "danger")
        return redirect(url_for('add_report'))

    flash(f"Berhasil! terdeteksi {num_detections} jalan berlubang", "success")
    return redirect(url_for('report_user'))


def user_report_delete(report_id):
    report = PotholeReportModel.query.filter_by(pothole_report_id=report_id).first()
    if not report:
        flash("Data tidak ditemukan!", "danger")
        return redirect(url_for('report_user'))

    # Tentukan path file gambarnya
    os.remove(os.path.join(Config.REPORT_FOLDER, report.image))
    db.session.delete(report)
    db.session.commit()
    flash("Data berhasil dihapus!", "success")
    return redirect(url_for('report_user'))