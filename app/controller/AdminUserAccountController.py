from app import app, db
from flask import request, render_template, redirect, url_for, session, flash
from app.model.UserModel import UserModel
from werkzeug.security import generate_password_hash, check_password_hash

def user_account():
    status_filter = request.args.get('status')
    if status_filter:
      users = UserModel.query.filter_by(status=status_filter).order_by(UserModel.user_id.desc())
    else:
      users = UserModel.query.order_by(UserModel.user_id.desc())

    return render_template('admin/user_account.html', users=users)

def user_account_edit(user_id):
    user = UserModel.query.get_or_404(user_id)
    return render_template('admin/user_account_edit.html', user=user)

def toggle_user_status(user_id):
    # Mengambil data user
    user = UserModel.query.filter_by(user_id=user_id).first()

    if not user:
        flash("Data tidak ditemukan!", "danger") 
        return redirect(url_for('user_account'))

    user.status = 0 if user.status == 1 else 1
    db.session.commit()
    return redirect(url_for('user_account'))



def admin_edit_user_profil_process():
    # request
    user_id = request.form['user_id']
    name = request.form['name']
    username = request.form['username']
    no_wa = request.form['no_wa']

    # Mengambil data admin
    user = UserModel.query.filter_by(user_id=user_id).first()
    if not user:
        flash("Data pengguna tidak ditemukan !", "danger")
        return redirect(url_for('user_account_edit',user_id=user.user_id))

    # Chek username jika sudah digunakan 
    check_username = UserModel.query.filter(UserModel.user_id != user_id, UserModel.username == username).first()
    if check_username:
        flash("Username sudah digunakan!", "danger")
        return redirect(url_for('user_account_edit',user_id=user.user_id))

    # Jika username tidak sama lakukan update
    if user.username != username:
        user.username = username
    
    # Chek no WA jika sudah digunakan 
    check_no_wa = UserModel.query.filter(UserModel.user_id != user_id, UserModel.no_wa == no_wa).first()
    if check_no_wa:
        flash("No WA sudah digunakan!", "danger")
        return redirect(url_for('user_account_edit',user_id=user.user_id))

    # Jika username tidak sama lakukan update
    if user.no_wa != no_wa:
        user.no_wa = no_wa
    
    # update user
    user.name = name
    user.no_wa = no_wa
    db.session.commit()

    # Ubah session saat ini
    flash("Berhasil update akun", "success")
    return redirect(url_for('user_account_edit',user_id=user.user_id))

def admin_reset_user_password_process():
    # request
    user_id = request.form['user_id']
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']

    # Mengambil data user
    user = UserModel.query.filter_by(user_id=user_id).first()

    if not user:
        flash("Data tidak ditemukan!", "danger") 
        return redirect(url_for('user_account'))

    # Cek password konfirmasi
    if password != password_confirmation:
        flash("Password konfirmasi dengan password tidak sama!", "danger")
        return redirect(url_for('user_account_edit',user_id=user.user_id))

    # Cek Jika Tidak Ada Data
    if not user:
        flash("Data pengguna tidak ditemukan !", "danger")
        return redirect(url_for('user_account_edit',user_id=user.user_id))

    # Update password
    user.password = generate_password_hash(password)
    db.session.commit()
    flash("Berhasil reset password !", "success")
    return redirect(url_for('user_account_edit',user_id=user.user_id))
