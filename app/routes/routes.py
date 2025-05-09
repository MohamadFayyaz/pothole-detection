from app import app
from app.middleware.middleware import guest_only,login_required,load_user,role_required
from flask import session, redirect, url_for, send_file
import os
from app.controller import UserPageController, UserAuthController, UserReportController, UserProfilController

# Home
@app.route('/')
def home():
    return UserPageController.page()
    
# Dashboard
@app.route('/dashboard')
@login_required
@role_required('user')
def dashboard_user():
    return UserPageController.dashboard()

# REPORT
@app.route('/report')
@login_required
@role_required('user')
def report_user():
    return UserReportController.report()

@app.route('/report/add-report')
@login_required
@role_required('user')
def add_report():
    return UserReportController.add_report()

@app.route('/report/delete/<int:report_id>', methods=['POST'])
@login_required
@role_required('user')
def user_report_delete(report_id):
    return UserReportController.user_report_delete(report_id)



@app.route('/geojson',methods=['POST'])
@login_required
@role_required('user')
def user_serve_geojson():
    geojson_path = os.path.join('protected_data', 'kordinat.geojson')
    return send_file(geojson_path, mimetype='application/json')

@app.route('/report/add-report-process',methods=['POST'])
@login_required
@role_required('user')
def add_report_process():
    return UserReportController.add_report_process()


# Auth

@app.route('/login')
@guest_only
def login():
    return UserAuthController.login()

@app.route('/login', methods=['POST'])
@guest_only
def login_process():
    return UserAuthController.login_process()

    
@app.route('/logout',methods=['GET'])
@login_required
@role_required('user')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/register')
@guest_only
def register():
    return UserAuthController.register()


@app.route('/register-process',methods=['POST'])
@guest_only
def register_process():
    return UserAuthController.register_process()



# Profil
@app.route('/profil')
@login_required
@role_required('user')
def profil():
    return UserAuthController.profil()

@app.route('/edit-profil-process',methods=['POST'])
@login_required
@role_required('user')
def edit_profil_process():
    return UserAuthController.edit_profil_process()

@app.route('/reset-password-process',methods=['POST'])
@login_required
@role_required('user')
def reset_password_process():
    return UserAuthController.reset_password_process()




# TEST MAP
@app.route('/maps')
def maps():
    return UserReportController.maps()