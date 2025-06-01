
from flask import Blueprint

# Creamos un Blueprint para las rutas
# Esto nos permite organizar las rutas en diferentes archivos
auth_bp = Blueprint('auth', __name__)
main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin') # Prefijo /admin para rutas de admin
