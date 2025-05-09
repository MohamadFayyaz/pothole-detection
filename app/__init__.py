from flask import Flask, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from ultralytics import YOLO

app = Flask(__name__)
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


from app.model import SurveyorModel,AdministratorModel,PotholeReportModel,PotholeSegmentModel,UserModel
from app.routes import routes, adminRoute
# Menjalankan aplikasi Flask
if __name__ == "__main__":
    try:
        app.run(use_reloader=False)  # use_reloader=False untuk mencegah aplikasi berjalan dua kali
    except Exception as e:
        print(f"Aplikasi mengalami kesalahan: {e}")