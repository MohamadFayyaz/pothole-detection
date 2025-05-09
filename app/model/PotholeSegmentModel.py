from app import db
from app.model.SurveyorModel import SurveyorModel

class PotholeSegmentModel(db.Model):

    __tablename__ = 'pothole_segments'

    pothole_segment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    surveyor_id = db.Column(db.Integer, db.ForeignKey(SurveyorModel.surveyor_id))
    datetime = db.Column(db.DateTime, nullable=False)
    latitude_awal = db.Column(db.DECIMAL(10, 8), nullable=False)
    longtitude_awal = db.Column(db.DECIMAL(11, 8), nullable=False)
    latitude_akhir = db.Column(db.DECIMAL(10, 8), nullable=False)
    longtitude_akhir = db.Column(db.DECIMAL(11, 8), nullable=False)
    number_potholes = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<PotholeSegmentModel {}>'.format(self.pothole_segment_id)