from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class AdministratorModel(db.Model):

    __tablename__ = 'administrators'

    administrator_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(250), index=True, nullable=False)
    no_wa = db.Column(db.String(250), index=True, unique=True, nullable=True)
    username = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    status = db.Column(db.Integer, nullable=False, server_default='1', default=1, comment="0: Tidak Aktif, 1: Aktif")

    def __repr__(self):
        return '<AdministratorModel {}>'.format(self.administrator_id)

    def setPassword(self, password):
        self.password = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.password, password)