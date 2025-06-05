# routes/main.py (Este maneja las rutas principales como el chat)

from flask import render_template, redirect, url_for, session, request, flash, current_app
from . import main_bp  # Importamos el Blueprint
from utilities import login_required  # Importamos el decorador
from models import db, User  # Para consultar y actualizar usuarios

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

   
@main_bp.route('/terms')
def terms():
    return render_template('legal/terms.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('legal/privacy.html')

# --- NUEVAS RUTAS PARA EL PERFIL ---

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if request.method == 'POST':
        # Aquí manejaremos la lógica de actualización del perfil
        # Por ahora, solo actualizaremos la bio
        new_bio = request.form.get('bio')
        if new_bio is not None:  # Permitir que sea vacío
            user.bio = new_bio
            db.session.commit()
            flash('Tu biografía ha sido actualizada.', 'success')

        # Lógica para subir foto de perfil (por ahora, solo una URL de ejemplo)
        # Esto es lo complejo y lo haremos en un paso posterior si quieres.
        # Por ahora, no lo procesaremos, pero prepararemos el campo en el HTML.

        return redirect(url_for('main.profile'))  # Redirigir para evitar reenvío de formulario

    return render_template('profile.html', user=user)

# Ruta para manejar la subida de foto de perfil (muy simplificada por ahora)
# Esta ruta es un placeholder. La implementación real de subida de archivos es más compleja.
@main_bp.route('/upload_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file.filename != '':
            # Aquí iría la lógica para guardar la imagen de forma segura
            # y obtener su URL. Por ahora, pondremos una URL estática/aleatoria.
            # En un entorno real, NO GUARDES ASÍ. Usa algo como Flask-Uploads o Cloudinary.

            # EJEMPLO SIMPLIFICADO: Generar una URL de placeholder o una URL fija
            # Para un proyecto real, necesitarías:
            # 1. Validar el tipo de archivo y tamaño.
            # 2. Guardar el archivo en un lugar seguro (ej. /static/uploads/profile_pics).
            # 3. Generar un nombre de archivo único para evitar colisiones.
            # 4. Actualizar user.profile_picture_url con la URL real.

            # Por ahora, solo para que no dé error:
            user.profile_picture_url = f"https://picsum.photos/id/{user.id}/150/150"  # Ejemplo de URL de placeholder
            db.session.commit()
            flash('Tu foto de perfil ha sido actualizada.', 'success')
        else:
            flash('No se seleccionó ningún archivo.', 'warning')
    else:
        flash('No se encontró el archivo de imagen en la solicitud.', 'error')

    return redirect(url_for('main.profile'))
