from app import app, db
from flask import request, render_template, redirect, url_for, session, flash
from app.model.AdministratorModel import AdministratorModel
from werkzeug.security import generate_password_hash, check_password_hash


def login():
    return render_template('admin/login.html')


def login_process():
    username = request.form['username']
    password = request.form['password']

    admin = AdministratorModel.query.filter_by(username=username).first()


    if not admin:
        flash("Username atau password salah!", "danger") 
        return redirect(url_for('login_admin'))

    if not admin.checkPassword(password):
        flash("Username atau password salah!", "danger") 
        return redirect(url_for('login_admin'))

    if admin.status == '0':
        flash("Akun anda sudah tidak aktif!", "danger") 
        return redirect(url_for('login_admin'))

    session['admin'] = {'name': admin.name,'username': username,'no_wa': admin.no_wa, 'role': 'admin','id':admin.administrator_id}
    flash("Berhasil Masuk!", "success")
    return redirect(url_for('dashboard_admin'))

def create_admin():
    name = 'admin'
    username = 'admin'
    no_wa = '083123'
    password = 'admin123'

    check_username = AdministratorModel.query.filter_by(username=username).first()
    if(check_username):
        flash("Username Sudah Digunakan!", "danger") 
        return redirect(url_for('register'))

    users = AdministratorModel(name=name, username=username, no_wa=no_wa)
    users.setPassword(password)
    db.session.add(users)
    db.session.commit()
    # return render_template('user/register.html')
    flash("Berhasil Registrasi!", "success")
    return redirect(url_for('login_admin'))


def profil():
    return render_template('admin/profil.html')

def admin_edit_profil_process():
    # request
    name = request.form['name']
    username = request.form['username']
    no_wa = request.form['no_wa']

    # Mengambil data admin
    admin = AdministratorModel.query.filter_by(administrator_id=session['admin']['id']).first()
    if not admin:
        flash("Data pengguna tidak ditemukan !", "danger")
        return redirect(url_for('admin_profil'))

    # Chek username jika sudah digunakan 
    check_username = AdministratorModel.query.filter(AdministratorModel.administrator_id != session['admin']['id'], AdministratorModel.username == username).first()
    if check_username:
        flash("Username sudah digunakan!", "danger")
        return redirect(url_for('admin_profil'))

    # Jika username tidak sama lakukan update
    if admin.username != username:
        admin.username = username
    
    # Chek no WA jika sudah digunakan 
    check_no_wa = AdministratorModel.query.filter(AdministratorModel.administrator_id != session['admin']['id'], AdministratorModel.no_wa == no_wa).first()
    if check_no_wa:
        flash("No WA sudah digunakan!", "danger")
        return redirect(url_for('admin_profil'))

    # Jika username tidak sama lakukan update
    if admin.no_wa != no_wa:
        admin.no_wa = no_wa
    
    # update user
    admin.name = name
    admin.no_wa = no_wa
    db.session.commit()

    # Ubah session saat ini
    session['admin']['name'] = name
    session['admin']['username'] = username
    session['admin']['no_wa'] = no_wa
    flash("Berhasil update profil", "success")
    return redirect(url_for('admin_profil'))

def admin_reset_password_process():
    # request
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']

    # Cek password konfirmasi
    if password != password_confirmation:
        flash("Password konfirmasi dengan password tidak sama!", "danger")
        return redirect(url_for('admin_profil'))

    # Mengambil data admin
    admin = AdministratorModel.query.filter_by(administrator_id=session['admin']['id']).first()
    if not admin:
        flash("Data pengguna tidak ditemukan !", "danger")
        return redirect(url_for('admin_profil'))

    # Update password
    admin.password = generate_password_hash(password)
    db.session.commit()
    flash("Berhasil reset password !", "success")
    return redirect(url_for('admin_profil'))
    