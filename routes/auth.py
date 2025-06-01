# routes/auth.py
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_mail import Message
from functools import wraps
import uuid
import datetime

from . import auth_bp
from models import db, User, ConfirmationToken
from utilities import login_required

# Función para enviar correo de confirmación
def send_confirmation_email(user, token_value):
    confirm_url = url_for('auth.confirm_email', token=token_value, _external=True)
    msg = Message("Confirma tu correo electrónico para Gatito Sentimental",
                  recipients=[user.email])
    msg.body = f"Hola {user.username},\\n\\nGracias por registrarte en Gatito Sentimental.\\nPor favor, haz clic en el siguiente enlace para confirmar tu correo electrónico: {confirm_url}\\n\\nEste enlace expirará en 1 hora.\\n\\nSaludos,\\nEl equipo de la Comunidad TikTok"
    try:
        current_app.mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error al enviar email a {user.email}: {e}")
        return False

@auth_bp.route('/register', methods=['POST'])
def register():
    # --- Protección Anti-bots (Honeypot) ---
    honeypot_field = request.form.get('honeypot_field')
    if honeypot_field: # Si este campo oculto se rellena, es probable que sea un bot
        current_app.logger.warning(f"Intento de registro de bot detectado para usuario: {request.form.get('username')}")
        flash('Error en el registro. Por favor, inténtalo de nuevo.', 'error') # Mensaje genérico para no dar pistas
        return redirect(url_for('main.index', show_register=True))

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if len(password) < 6:
        flash('La contraseña debe tener al menos 6 caracteres.', 'error')
        return redirect(url_for('main.index', show_register=True))

    if password != confirm_password:
        flash('Las contraseñas no coinciden', 'error')
        return redirect(url_for('main.index', show_register=True))

    existing_user = User.query.filter_by(username=username).first()
    existing_email = User.query.filter_by(email=email).first()

    if existing_user:
        flash('El nombre de usuario ya existe. Por favor, elige otro.', 'error')
        return redirect(url_for('main.index', show_register=True))
    if existing_email:
        flash('Este correo electrónico ya está registrado.', 'error')
        return redirect(url_for('main.index', show_register=True))

    new_user = User(username=username, email=email, email_confirmed=False)
    new_user.set_password(password)

    # El primer usuario que se registre será admin por defecto
    if User.query.count() == 0:
        new_user.role = 'admin'

    db.session.add(new_user)
    db.session.commit()

    token_value = str(uuid.uuid4())
    new_token = ConfirmationToken(user_id=new_user.id, token=token_value)
    db.session.add(new_token)
    db.session.commit()

    if send_confirmation_email(new_user, token_value):
        flash('¡Registro exitoso! Por favor, revisa tu correo electrónico para confirmar tu cuenta.', 'success')
    else:
        flash('Registro exitoso, pero hubo un problema al enviar el correo de confirmación. Por favor, contáctanos.', 'error')

    return redirect(url_for('main.index', show_register=True))

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    # --- Protección contra Ataques de Fuerza Bruta ---
    if user and user.locked_until and user.locked_until > datetime.datetime.now():
        remaining_time = user.locked_until - datetime.datetime.now()
        minutes = int(remaining_time.total_seconds() / 60)
        seconds = int(remaining_time.total_seconds() % 60)
        flash(f'Tu cuenta está bloqueada debido a demasiados intentos fallidos. Intenta de nuevo en {minutes} minutos y {seconds} segundos.', 'error')
        return redirect(url_for('main.index'))

    if not user or not user.check_password(password):
        if user: # Si el usuario existe pero la contraseña es incorrecta
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= current_app.config['LOGIN_ATTEMPTS_LIMIT']:
                user.locked_until = datetime.datetime.now() + datetime.timedelta(minutes=current_app.config['LOCKOUT_DURATION_MINUTES'])
                flash(f'Demasiados intentos de inicio de sesión fallidos. Tu cuenta ha sido bloqueada por {current_app.config["LOCKOUT_DURATION_MINUTES"]} minutos.', 'error')
                current_app.logger.warning(f"Cuenta de usuario {user.username} bloqueada por fuerza bruta.")
            else:
                flash(f'Nombre de usuario o contraseña incorrectos. Te quedan {current_app.config["LOGIN_ATTEMPTS_LIMIT"] - user.failed_login_attempts} intentos.', 'error')
            db.session.commit()
        else: # Si el usuario no existe
            flash('Nombre de usuario o contraseña incorrectos.', 'error')
        return redirect(url_for('main.index'))

    # Si la contraseña es correcta
    if not user.email_confirmed:
        flash('Tu correo electrónico no ha sido confirmado. Por favor, revisa tu bandeja de entrada.', 'error')
        return redirect(url_for('main.index'))

    # Restablecer intentos fallidos y bloqueo al iniciar sesión exitosamente
    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()

    session['user_id'] = user.id
    session['username'] = user.username
    session['user_role'] = user.role
    session['email_confirmed'] = user.email_confirmed
    flash('Inicio de sesión exitoso.', 'success')
    return redirect(url_for('main.chat'))

@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('email_confirmed', None)
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/confirm_email/<token>')
def confirm_email(token):
    confirmation_token = ConfirmationToken.query.filter_by(token=token).first()

    if not confirmation_token:
        flash('Enlace de confirmación inválido o ya usado.', 'error')
        return redirect(url_for('main.index'))

    if confirmation_token.expires_at < datetime.datetime.now():
        flash('El enlace de confirmación ha expirado. Por favor, regístrate de nuevo o solicita otro.', 'error')
        db.session.delete(confirmation_token)
        db.session.commit()
        return redirect(url_for('main.index'))

    user = User.query.get(confirmation_token.user_id)
    if user and not user.email_confirmed:
        user.email_confirmed = True
        db.session.delete(confirmation_token)
        db.session.commit()

        # --- Inicio de Sesión Automático tras Confirmación ---
        session['user_id'] = user.id
        session['username'] = user.username
        session['user_role'] = user.role
        session['email_confirmed'] = user.email_confirmed
        flash('¡Tu correo electrónico ha sido confirmado exitosamente! Has iniciado sesión automáticamente.', 'success')
        return redirect(url_for('main.chat'))
    elif user and user.email_confirmed:
        flash('Tu correo ya ha sido confirmado previamente. Ya puedes iniciar sesión.', 'info')
        return redirect(url_for('main.index')) # O redirigir al chat si ya estaba logueado
    else:
        flash('Error al confirmar tu correo electrónico. Usuario no encontrado.', 'error')
        return redirect(url_for('main.index'))
