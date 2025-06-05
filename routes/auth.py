# routes/auth.py
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_mail import Message
from functools import wraps
import uuid
import datetime

from . import auth_bp
from models import db, User, ConfirmationToken, PasswordResetToken
from utilities import login_required

def send_confirmation_email(user, token_value):
    confirm_url = url_for('auth.confirm_email', token=token_value, _external=True)
    msg = Message("Confirma tu correo electrónico para Gatito Sentimental",
                  recipients=[user.email])
    msg.html = render_template('emails/confirm_email.html', username=user.username, confirm_url=confirm_url)
    msg.body = f"Hola {user.username},\n\nGracias por registrarte en Gatito Sentimental.\nPor favor, haz clic en el siguiente enlace para confirmar tu correo electrónico: {confirm_url}\n\nEste enlace expirará en 1 hora.\n\nSaludos,\nGatito Sentimental"
    try:
        current_app.mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error al enviar email a {user.email}: {e}")
        return False
        
def send_welcome_email(user):
    msg = Message("¡Bienvenido a Gatito Sentimental!",
                  recipients=[user.email])
    msg.html = render_template('emails/welcome_email.html', username=user.username)
    msg.body = f"Hola {user.username},\\n\\n¡Bienvenido a la comunidad de Gatito Sentimental!\\n\\nGracias por registrarte.\\n\\nSaludos,\\nGatito Sentimental" # Texto plano como respaldo
    try:
        current_app.mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error al enviar email de bienvenida a {user.email}: {e}")
        return False        

@auth_bp.route('/register', methods=['POST'])
def register():
    # --- Protección Anti-bots (Honeypot) ---
    honeypot_field = request.form.get('honeypot_field')
    if honeypot_field:
        current_app.logger.warning(f"Intento de registro de bot detectado para usuario: {request.form.get('username')}")
        flash('Error en el registro. Por favor, inténtalo de nuevo.', 'error')
        return redirect(url_for('main.index', show_register=True))

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    terms_accepted = request.form.get('terms') # Obtener el valor del campo 'terms'

    if not terms_accepted:
        flash('Debes aceptar los términos de uso y la política de privacidad para registrarte.', 'error')
        return redirect(url_for('main.index', show_register=True))

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
        send_welcome_email(new_user)
    else:
        flash('Registro exitoso, pero hubo un problema al enviar el correo de confirmación. Por favor, contáctanos.', 'error')
        send_welcome_email(new_user)

    return redirect(url_for('main.index', show_register=True))


@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and user.locked_until and user.locked_until > datetime.datetime.now():
        remaining_time = user.locked_until - datetime.datetime.now()
        minutes = int(remaining_time.total_seconds() / 60)
        seconds = int(remaining_time.total_seconds() % 60)
        flash(f'Tu cuenta está bloqueada debido a demasiados intentos fallidos. Intenta de nuevo en {minutes} minutos y {seconds} segundos.', 'error')
        return redirect(url_for('main.index'))

    if not user or not user.check_password(password):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= current_app.config['LOGIN_ATTEMPTS_LIMIT']:
                user.locked_until = datetime.datetime.now() + datetime.timedelta(minutes=current_app.config['LOCKOUT_DURATION_MINUTES'])
                flash(f'Demasiados intentos fallidos. Tu cuenta ha sido bloqueada por {current_app.config["LOCKOUT_DURATION_MINUTES"]} minutos.', 'error')
                current_app.logger.warning(f"Cuenta de usuario {user.username} bloqueada por fuerza bruta.")
            else:
                flash(f'Nombre de usuario o contraseña incorrectos. Te quedan {current_app.config["LOGIN_ATTEMPTS_LIMIT"] - user.failed_login_attempts} intentos.', 'error')
            db.session.commit()
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'error')
        return redirect(url_for('main.index'))

    if not user.email_confirmed:
        flash('Tu correo electrónico no ha sido confirmado. Por favor, revisa tu bandeja de entrada.', 'error')
        return redirect(url_for('main.index'))

    user.failed_login_attempts = 0
    user.locked_until = None
    db.session.commit()

    session['user_id'] = user.id
    session['username'] = user.username
    session['user_role'] = user.role
    session['email_confirmed'] = user.email_confirmed
    # --- Establecer la sesión como permanente ---
    session.permanent = True
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

        session['user_id'] = user.id
        session['username'] = user.username
        session['user_role'] = user.role
        session['email_confirmed'] = user.email_confirmed
        flash('¡Tu correo electrónico ha sido confirmado exitosamente! Has iniciado sesión automáticamente.', 'success')
        return redirect(url_for('main.chat'))
    elif user and user.email_confirmed:
        flash('Tu correo ya ha sido confirmado previamente. Ya puedes iniciar sesión.', 'info')
        return redirect(url_for('main.index'))
    else:
        flash('Error al confirmar tu correo electrónico. Usuario no encontrado.', 'error')
        return redirect(url_for('main.index'))

def send_password_reset_email(user, token_value):
    reset_url = url_for('auth.reset_password', token=token_value, _external=True)
    msg = Message("Restablece tu contraseña para Gatito Sentimental",
                  recipients=[user.email])
    msg.html = render_template('emails/reset_password_email.html', username=user.username, reset_url=reset_url)
    msg.body = f"Hola {user.username},\n\nHas solicitado restablecer tu contraseña para Gatito Sentimental.\nPor favor, haz clic en el siguiente enlace para crear una nueva contraseña: {reset_url}\n\nEste enlace expirará en 1 hora.\n\nSi no solicitaste este restablecimiento, puedes ignorar este correo.\n\nSaludos,\nGatito Sentimental"
    try:
        current_app.mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error al enviar email de restablecimiento a {user.email}: {e}")
        return False

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token_value = str(uuid.uuid4())
            expires_at = datetime.datetime.now() + datetime.timedelta(hours=1)
            reset_token = PasswordResetToken(user_id=user.id, token=token_value, expires_at=expires_at)
            db.session.add(reset_token)
            db.session.commit()

            if send_password_reset_email(user, token_value):
                flash('Se ha enviado un enlace para restablecer tu contraseña a tu correo electrónico.', 'info')
                return redirect(url_for('main.index'))
            else:
                flash('Hubo un problema al enviar el correo de restablecimiento. Por favor, inténtalo de nuevo más tarde.', 'error')
                return render_template('auth/forgot_password.html') # Renderizar de nuevo el formulario
        else:
            flash('No se encontró ninguna cuenta con esa dirección de correo electrónico.', 'warning')
            return render_template('auth/forgot_password.html') # Renderizar de nuevo el formulario
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token:
        flash('Enlace de restablecimiento de contraseña inválido o ya usado.', 'error')
        return redirect(url_for('main.index'))

    if reset_token.expires_at < datetime.datetime.now():
        flash('El enlace de restablecimiento de contraseña ha expirado. Por favor, solicita otro.', 'error')
        db.session.delete(reset_token)
        db.session.commit()
        return redirect(url_for('auth.forgot_password'))

    user = User.query.get(reset_token.user_id)
    if not user:
        flash('Error al restablecer la contraseña. Usuario no encontrado.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if len(new_password) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('auth/reset_password.html', token=token)
        if new_password != confirm_password:
            flash('Las nuevas contraseñas no coinciden.', 'error')
            return render_template('auth/reset_password.html', token=token)

        user.set_password(new_password)
        db.session.delete(reset_token)
        db.session.commit()
        flash('Tu contraseña ha sido restablecida exitosamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('main.index'))

    return render_template('auth/reset_password.html', token=token)
