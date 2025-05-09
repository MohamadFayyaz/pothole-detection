from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.model.AdministratorModel import AdministratorModel

class SurveyorModel(db.Model):

    __tablename__ = 'surveyors'

    surveyor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    administrator_id = db.Column(db.Integer, db.ForeignKey(AdministratorModel.administrator_id))
    name = db.Column(db.String(250), index=True, nullable=False)
    no_wa = db.Column(db.String(250), index=True, unique=True, nullable=False)
    username = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return '<SurveyorModel {}>'.format(self.surveyor_id)

    def setPassword(self, password):
        self.password = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.password, password)