# utilities.py
from flask import redirect, url_for, flash, session
from functools import wraps
from models import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Necesitas iniciar sesión para acceder a esta página.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_role') != 'admin':
            flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
            return redirect(url_for('main.chat'))
        return f(*args, **kwargs)
    return decorated_function
