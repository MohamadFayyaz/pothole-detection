from app import db
from app.model.AdministratorModel import AdministratorModel
from app.model.UserModel import UserModel

class PotholeReportModel(db.Model):

    __tablename__ = 'pothole_reports'

    pothole_report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(UserModel.user_id))
    administrator_id = db.Column(db.Integer, db.ForeignKey(AdministratorModel.administrator_id),nullable=True)
    datetime = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.DECIMAL(10, 8), nullable=False)
    longtitude = db.Column(db.DECIMAL(11, 8), nullable=False)
    number_potholes = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    kecamatan = db.Column(db.String(250), nullable=False)
    status = db.Column(db.Enum("selesai", "proses", "ditolak", name="status_report"), nullable=False)

    def __repr__(self):
        return '<PotholeReportModel {}>'.format(self.pothole_report_id)