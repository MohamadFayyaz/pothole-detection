from flask import Flask, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from ultralytics import YOLO
from flask import request
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.exceptions import HTTPException
import os
import re
from flask import request

# Pastikan direktori log ada
if not os.path.exists('logs'):
    os.makedirs('logs')

log_path = os.path.join('logs', 'flask_app.log')

# Setup logging
handler = RotatingFileHandler(log_path, maxBytes=1000000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)


app = Flask(__name__)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
csrf = CSRFProtect(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

first_request = True

@app.before_request
def load_model():
    global first_request
    if first_request:
        # Fungsi untuk memuat model YOLO
        app.yolo_model = YOLO('best.pt')
        first_request = False


from app.model import AdministratorModel,PotholeReportModel,UserModel
from app.routes import routes, adminRoute

#Error Handler 404
@app.errorhandler(404)
def page_not_found(e):
    return {'message': 'Halaman tidak ditemukan'}, 404

@app.errorhandler(500)
def internal_server_error(e):
    return {'message': 'Terjadi kesalahan di server'}, 500


# Log
@app.before_request
def log_request_info():
    app.logger.info(f"REQUEST: {request.method} {request.url} | IP: {request.remote_addr}")

@app.after_request
def log_response_info(response):
    app.logger.info(f"RESPONSE: {request.method} {request.url} -> {response.status}")
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    # biarkan Flask tangani sesuai status code
    if isinstance(e, HTTPException):
        return e  
    
    app.logger.error(f"ERROR: {request.method} {request.url} | {str(e)}", exc_info=True)
    return {"message": "Terjadi kesalahan di server"}, 500

# Menjalankan aplikasi Flask
if __name__ == "__main__":
    try:
        app.run(use_reloader=False)  # use_reloader=False untuk mencegah aplikasi berjalan dua kali
    except Exception as e:
        print(f"Aplikasi mengalami kesalahan: {e}")