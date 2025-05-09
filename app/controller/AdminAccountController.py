from app import app, db
from flask import request, render_template, redirect, url_for, session, flash
from app.model.AdministratorModel import AdministratorModel
from werkzeug.security import generate_password_hash, check_password_hash
import pdb

def admin_account():
    status_filter = request.args.get('status')
    if status_filter:
      admins = AdministratorModel.query.filter(
        AdministratorModel.status == status_filter,
        AdministratorModel.administrator_id != session['admin']['id']
        ).order_by(AdministratorModel.administrator_id.desc()).all()
    else:
      admins = AdministratorModel.query.filter(AdministratorModel.administrator_id != session['admin']['id']).order_by(AdministratorModel.administrator_id.desc())

    return render_template('admin/admin_account.html', admins=admins)

def admin_account_edit(admin_id):
    admin = AdministratorModel.query.get_or_404(admin_id)
    return render_template('admin/admin_account_edit.html', admin=admin)

def toggle_admin_status(admin_id):
    # Mengambil data admin
    admin = AdministratorModel.query.filter_by(administrator_id=admin_id).first()

    if not admin:
        flash("Data tidak ditemukan!", "danger") 
        return redirect(url_for('admin_account'))
    admin.status = 0 if admin.status == 1 else 1
    db.session.commit()
    return redirect(url_for('admin_account'))



def edit_admin_profil_process():
    # request
    admin_id = request.form['admin_id']
    name = request.form['name']
    username = request.form['username']
    no_wa = request.form['no_wa']

    # Mengambil data admin
    admin = AdministratorModel.query.filter_by(administrator_id=admin_id).first()

    if not admin:
        flash("Data tidak ditemukan!", "danger") 
        return redirect(url_for('admin_account'))

    if not admin:
        flash("Data pengguna tidak ditemukan !", "danger")
        return redirect(url_for('admin_account_edit',admin_id=admin.administrator_id))

    # Chek username jika sudah digunakan 
    check_username = AdministratorModel.query.filter(AdministratorModel.administrator_id != admin_id, AdministratorModel.username == username).first()
    if check_username:
        flash("Username sudah digunakan!", "danger")
        return redirect(url_for('admin_account_edit',admin_id=admin.administrator_id))

    # Jika username tidak sama lakukan update
    if admin.username != username:
        admin.username = username
    
    # Chek no WA jika sudah digunakan 
    check_no_wa = AdministratorModel.query.filter(AdministratorModel.administrator_id != admin_id, AdministratorModel.no_wa == no_wa).first()
    if check_no_wa:
        flash("No WA sudah digunakan!", "danger")
        return redirect(url_for('admin_account_edit',admin_id=admin.administrator_id))

    # Jika username tidak sama lakukan update
    if admin.no_wa != no_wa:
        admin.no_wa = no_wa
    
    
    # update user
    admin.name = name
    admin.no_wa = no_wa
    db.session.commit()

    # Ubah session saat ini
    flash("Berhasil update akun", "success")
    return redirect(url_for('admin_account_edit',admin_id=admin.administrator_id))

def reset_admin_password_process():
    # request
    admin_id = request.form['admin_id']
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']

    # Mengambil data admin
    admin = AdministratorModel.query.filter_by(administrator_id=admin_id).first()

    if not admin:
        flash("Data tidak ditemukan!", "danger") 
        return redirect(url_for('admin_account'))

    # Cek password konfirmasi
    if password != password_confirmation:
        flash("Password konfirmasi dengan password tidak sama!", "danger")
        return redirect(url_for('admin_account_edit',admin_id=admin.administrator_id))

    # jika tidak ada data akun
    if not admin:
        flash("Data pengguna tidak ditemukan !", "danger")
        return redirect(url_for('admin_account_edit',admin_id=admin.administrator_id))

    # Update password
    admin.password = generate_password_hash(password)
    db.session.commit()
    flash("Berhasil reset password !", "success")
    return redirect(url_for('admin_account_edit',admin_id=admin.administrator_id))


def create_admin():
        return render_template('admin/admin_account_add.html')

def create_admin_process():
    name = request.form['name']
    username = request.form['username']
    no_wa = request.form['no_wa']
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']

    # Cek password konfirmasi
    if password != password_confirmation:
        flash("Password konfirmasi dengan password tidak sama!", "danger")
        return redirect(url_for('create_admin'))

    check_username = AdministratorModel.query.filter_by(username=username).first()
    if(check_username):
        flash("Username Sudah Digunakan!", "danger") 
        return redirect(url_for('create_admin'))

    # Cek No WA
    check_no_wa = AdministratorModel.query.filter(AdministratorModel.no_wa==no_wa).first()
    if(check_no_wa):
        flash("No WA Sudah Digunakan!", "danger") 
        return redirect(url_for('create_admin'))
    if(no_wa == ''):
        no_wa = None

    admin = AdministratorModel(name=name, username=username, no_wa=no_wa)
    admin.setPassword(password)
    db.session.add(admin)
    db.session.commit()
    flash("Berhasil Membuat Akun Administrator!", "success")
    return redirect(url_for('admin_account'))