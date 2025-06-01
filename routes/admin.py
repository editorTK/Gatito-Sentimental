
from flask import render_template, redirect, url_for, flash, session
from . import admin_bp # Importamos el Blueprint
from models import db, User # Importamos los modelos
from utilities import login_required, admin_required # Importamos los decoradores

@admin_bp.route('/manage_users')
@admin_required # Solo administradores pueden acceder a esta página
@login_required # También debe estar logueado
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@admin_bp.route('/set_role/<int:user_id>/<string:role_name>', methods=['POST'])
@admin_required # Solo administradores pueden cambiar roles
@login_required
def set_user_role(user_id, role_name):
    user = User.query.get_or_404(user_id)
    if role_name not in ['user', 'admin']:
        flash('Rol no válido.', 'error')
        return redirect(url_for('admin.manage_users'))

    # Evitar que un admin se quite a sí mismo el rol de admin si es el único
    if user.id == session.get('user_id') and role_name == 'user':
        # Contar cuántos admins hay
        admin_count = User.query.filter_by(role='admin').count()
        if admin_count <= 1:
            flash('No puedes quitarte el rol de administrador si eres el único.', 'error')
            return redirect(url_for('admin.manage_users'))

    user.role = role_name
    db.session.commit()
    flash(f'El rol de {user.username} ha sido actualizado a {role_name}.', 'success')
    return redirect(url_for('admin.manage_users'))
