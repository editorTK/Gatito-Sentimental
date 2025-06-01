
from flask import render_template, redirect, url_for, session, request, flash
from . import main_bp # Importamos el Blueprint
from utilities import login_required # Importamos el decorador

@main_bp.route('/')
def index():
    # Si el usuario ya está logueado Y tiene el email confirmado, lo redirigimos al chat
    if 'username' in session and session.get('email_confirmed'):
        return redirect(url_for('main.chat'))
    # Si viene de un error de registro, mostrar el formulario de registro
    if request.args.get('show_register'):
        return render_template('index.html', show_register=True)
    return render_template('index.html')

@main_bp.route('/chat')
@login_required # Protegemos la ruta del chat
def chat():
    # Asegurarse de que el correo esté confirmado para acceder al chat
    if not session.get('email_confirmed'):
        flash('Necesitas confirmar tu correo electrónico para acceder al chat. Revisa tu bandeja de entrada.', 'error')
        return redirect(url_for('main.index'))
    return render_template('chat.html', username=session['username'])
