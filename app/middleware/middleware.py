from app import app
from flask import session, redirect, url_for, g, flash
from functools import wraps

# Middleware: login required
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            flash("Silahkan masuk terlebih dahulu!", "danger")
            return redirect(url_for('login_admin'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware: hanya untuk guest (belum login)
def admin_guest_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' in session:
            flash("Silahkan keluar terlebih dahulu!", "danger")
            return redirect(url_for('dashboard_admin'))
        return f(*args, **kwargs)
    return decorated_function
    

    
# Middleware: cek role
def admin_role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'admin' not in session or session['admin']['role'] != role:
                return "Unauthorized", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Middleware: login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Silahkan masuk terlebih dahulu!", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware: hanya untuk guest (belum login)
def guest_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' in session:
            flash("Silahkan keluar terlebih dahulu!", "danger")
            return redirect(url_for('dashboard_user'))
        return f(*args, **kwargs)
    return decorated_function

# Middleware: cek role
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session or session['user']['role'] != role:
                return "Unauthorized", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.before_request
def load_user():
    g.user = session.get('user')
