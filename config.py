import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    HOST = str(os.environ.get("DB_HOST"))
    DATABASE = str(os.environ.get("DB_DATABASE"))
    USERNAME = str(os.environ.get("DB_USERNAME"))
    PASSWORD = str(os.environ.get("DB_PASSWORD"))

    SECRET_KEY = str(os.environ.get("JWT_SECRET"))

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + USERNAME + ':' + PASSWORD + '@' + HOST + '/' + DATABASE
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
#     project_id= os.environ.get('project_id')
# auth_uri=os.environ.get('auth_uri')
# token_uri=os.environ.get('token_uri')
# auth_provider_x509_cert_url="https://www.googleapis.com/oauth2/v1/certs",

    MAP_SERVICE_API_KEY = str(os.environ.get("MAP_SERVICE_API_KEY"))

    REPORT_FOLDER = str(os.environ.get("REPORT_FOLDER"))
