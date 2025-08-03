from app import app, db, oauth
from flask import request, render_template, redirect, url_for, session, flash
from app.model.UserModel import UserModel
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config


def register():
    return render_template('user/register.html')

def register_process():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']

    if(password != password_confirmation):
        flash("Konfirmasi Password Tidak Cocok!", "danger") 
        return redirect(url_for('register'))

    check_username = UserModel.query.filter_by(username=username).first()
    if(check_username):
        flash("Username Sudah Digunakan!", "danger") 
        return redirect(url_for('register'))

    # check_no_wa = UserModel.query.filter_by(no_wa=no_wa).first()
    # if(check_no_wa):
    #     flash("No WA Sudah Digunakan!", "danger") 
    #     return redirect(url_for('register'))

    users = UserModel(name=name, username=username)
    users.setPassword(password)
    db.session.add(users)
    db.session.commit()
    # return render_template('user/register.html')
    flash("Berhasil Registrasi!", "success")
    return redirect(url_for('login'))

def login():
    return render_template('user/login.html')

def profil():
    return render_template('user/profil.html')

def edit_profil_process():
    # request
    name = request.form['name'] or None
    username = request.form['username'] or None
    no_wa = request.form['no_wa'] or None
    address = request.form['address'] or None

    # Mengambil data admin
    user = UserModel.query.filter_by(user_id=session['user']['id']).first()
    if not user:
        flash("Data pengguna tidak ditemukan !", "danger")
        return redirect(url_for('profil'))

    # Chek username jika sudah digunakan 
    check_username = UserModel.query.filter(UserModel.user_id != session['user']['id'], UserModel.username == username).first()
    if username != None and check_username:
        flash("Username sudah digunakan!", "danger")
        return redirect(url_for('profil'))

    # Jika username tidak sama lakukan update
    if user.username != username:
        user.username = username

    # Chek no WA jika sudah digunakan
    check_no_wa = UserModel.query.filter(UserModel.user_id != session['user']['id'], UserModel.no_wa == no_wa).first()
    if no_wa != None and check_no_wa:
        print("test wa",check_no_wa.no_wa)
        print("test wa",no_wa)
        flash("No WA sudah digunakan!", "danger")
        return redirect(url_for('profil',user_id=user.user_id))

    # Jika username tidak sama lakukan update
    if user.no_wa != no_wa:
        user.no_wa = no_wa
    
    # update user
    user.name = name
    user.no_wa = no_wa
    user.address = address
    db.session.commit()

    # Ubah session saat ini
    session['user']['name'] = name
    session['user']['username'] = username
    session['user']['address'] = address
    flash("Berhasil update profil", "success")
    return redirect(url_for('profil'))

def reset_password_process():
    # request
    password = request.form['password']
    password_confirmation = request.form['password_confirmation']

    # Cek password konfirmasi
    if password != password_confirmation:
        flash("Password konfirmasi dengan password tidak sama!", "danger")
        return redirect(url_for('profil'))

    # Mengambil data user
    user = UserModel.query.filter_by(user_id=session['user']['id']).first()
    if not user:
        flash("Data pengguna tidak ditemukan !", "danger")
        return redirect(url_for('profil'))

    # Update password
    user.password = generate_password_hash(password)
    db.session.commit()
    flash("Berhasil reset password !", "success")
    return redirect(url_for('profil'))


def login_process():
    username = request.form['username']
    password = request.form['password']

    user = UserModel.query.filter_by(username=username).first()

    if not user:
        flash("Username atau password salah!", "danger")  
        return redirect(url_for('login'))

    if not user.checkPassword(password):
        flash("Username atau password salah!", "danger")  
        return redirect(url_for('login'))

    if user.status == '0':
        flash("Pengguna sudah tidak aktif!", "danger")  
        return redirect(url_for('login'))

    session['user'] = {
        'google_id': user.google_id,
        'name': user.name,
        'id':user.user_id,
        'username': username,
        'email': user.email,
        'address': user.address,
        'no_wa': user.no_wa,
        'role': 'user'
        }
    print(session['user'])
    flash("Berhasil Masuk!", "success")
    return redirect(url_for('dashboard_user'))

def google_login():
    
    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

def google_login_process():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()

    # Handle login/register logic
    email = user_info['email']

    user = UserModel.query.filter_by(email=email).first()

    # Kondisi jika seseorang belum punya akun, sehingga membuat akun baru dengan google
    if user is None:
        # Cek jika seseorang menghubungkan akunnya dengan google di halaman profil
        # jika akun google belum terpakai maka update profil 
        if 'user' in session:
            # update user
            userNow = UserModel.query.filter_by(user_id=session['user']['id']).first()
            userNow.email = user_info.get('email')
            userNow.google_id = user_info.get('id')
            db.session.commit()
            # update session
            session['user']['google_id']=user_info.get('id')
            session['user']['email']=user_info.get('email')
            
            flash("Berhasil terhubung dengan google", "success")
            return redirect(url_for('profil'))
        
        
        # Register user
        user = UserModel(email=user_info.get('email'), name=user_info.get('name'), google_id=user_info.get('id'))
        db.session.add(user)
        db.session.commit()

    # Cek jika seseorang menghubungkan akunnya dengan google di halaman profil
    # jika akun google sudah dipakai kirim notif 
    if user and 'user' in session and user.user_id != session['user']['id']:
        flash("Akun google sudah dipakai!", "danger")
        return redirect(url_for('profil'))

    # Kondisi jika seseorang belum login, sehingga login lewat google
    # Simpan ke session
    session['user'] = {
        'google_id': user.google_id,
        'name': user.name,
        'id':user.user_id,
        'username': user.username,
        'email': user.email,
        'address': user.address,
        'no_wa': user.no_wa,
        'role': 'user'
    }
    return redirect(url_for('dashboard_user'))