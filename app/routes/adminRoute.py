from app import app
from app.middleware.middleware import admin_guest_only,admin_login_required,load_user,admin_role_required
from flask import session, redirect, url_for, jsonify, send_file
import os
from app.controller import AdminAccountController, AdminAuthController,AdminDashboardController,AdminReportController,AdminUserAccountController, AdminRecapController


# AUTH

@app.route('/admin')
@admin_guest_only
def login_admin():
    return AdminAuthController.login()

@app.route('/admin',methods=['POST'])
@admin_guest_only
def login_admin_proses():
    return AdminAuthController.login_process()

@app.route('/admin/logout',methods=['GET'])
@admin_login_required
@admin_role_required('admin')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('login_admin'))

    
    


# REPORT
@app.route('/admin/report')
@admin_login_required
@admin_role_required('admin')
def report_admin():
    return AdminReportController.report()

@app.route('/admin/report/update-status/<int:report_id>', methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def update_report_status(report_id):
    return AdminReportController.update_report_status(report_id)

@app.route('/admin/report/delete/<int:report_id>', methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def report_delete(report_id):
    return AdminReportController.report_delete(report_id)





# DASHBOARD
@app.route('/admin/dashboard')
@admin_login_required
@admin_role_required('admin')
def dashboard_admin():
    return AdminDashboardController.dashboard()

@app.route('/admin/chart', methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def chart():
    return AdminDashboardController.chart()

@app.route('/admin/yearly-reports',methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def yearly_reports():
    return AdminDashboardController.yearly_reports()

@app.route('/admin/geojson',methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def serve_geojson():
    geojson_path = os.path.join('protected_data', 'kordinat.geojson')
    return send_file(geojson_path, mimetype='application/json')

@app.route('/admin/dashboard/report/update-status/<int:report_id>', methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def update_report_dashboard_status(report_id):
    return AdminDashboardController.update_report_dashboard_status(report_id)

@app.route('/admin/dashboard/report/delete/<int:report_id>', methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def report_dashboard_delete(report_id):
    return AdminDashboardController.report_dashboard_delete(report_id)





# Profil
@app.route('/admin/profil')
@admin_login_required
@admin_role_required('admin')
def admin_profil():
    return AdminAuthController.profil()

@app.route('/admin/edit-profil-process',methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def admin_edit_profil_process():
    return AdminAuthController.admin_edit_profil_process()

@app.route('/admin/reset-password-process',methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def admin_reset_password_process():
    return AdminAuthController.admin_reset_password_process()







# USER ACCOUNT
@app.route('/admin/user-account')
@admin_login_required
@admin_role_required('admin')
def user_account():
    return AdminUserAccountController.user_account()

@app.route('/admin/user-account/update-status/<int:user_id>', methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def toggle_user_status(user_id):
    return AdminUserAccountController.toggle_user_status(user_id)
    
@app.route('/admin/user-account/<int:user_id>')
@admin_login_required
@admin_role_required('admin')
def user_account_edit(user_id):
    return AdminUserAccountController.user_account_edit(user_id)


@app.route('/admin/admin-edit-user-profil-process', methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def admin_edit_user_profil_process():
    return AdminUserAccountController.admin_edit_user_profil_process()

@app.route('/admin/admin-reset-user-password-process', methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def admin_reset_user_password_process():
    return AdminUserAccountController.admin_reset_user_password_process()






# ADMIN ACCOUNT
@app.route('/admin/admin-account')
@admin_login_required
@admin_role_required('admin')
def admin_account():
    return AdminAccountController.admin_account()


# @app.route('/admin/edit-admin', methods=['POST'])
# @admin_login_required
# @admin_role_required('admin')
# def asd():
#     return AdminAccountController.edit_admin_profil_process()
@app.route('/admin/edit-admin',methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def asd():
    # return 'asd'    
    return AdminAccountController.edit_admin_profil_process()

@app.route('/admin/admin-account/update-status/<int:admin_id>', methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def toggle_admin_status(admin_id):
    return AdminAccountController.toggle_admin_status(admin_id)

@app.route('/admin/admin-account/add')
@admin_login_required
@admin_role_required('admin')
def create_admin():
    return AdminAccountController.create_admin()

@app.route('/create-admin-process',methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def create_admin_process():
    return AdminAccountController.create_admin_process()

@app.route('/admin/admin-account/<int:admin_id>')
@admin_login_required
@admin_role_required('admin')
def admin_account_edit(admin_id):
    return AdminAccountController.admin_account_edit(admin_id)

@app.route('/admin/reset-admin-password-process',methods=['POST'])
@admin_login_required
@admin_role_required('admin')
def reset_admin_password_process():
    return AdminAccountController.reset_admin_password_process()





# RECAP
@app.route('/admin/recap')
@admin_login_required
@admin_role_required('admin')
def recap():
    return AdminRecapController.recap()

@app.route('/admin/recap/process', methods=['post'])
@admin_login_required
@admin_role_required('admin')
def recap_process():
    return AdminRecapController.recap_process()