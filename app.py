# app.py (Este es el archivo principal que inicia todo)

from flask import Flask, session, current_app, jsonify # Agregamos jsonify para un posible uso futuro si lo necesitas

from flask_mail import Mail

from flask_socketio import SocketIO

import logging

from config import Config

from models import db, User # Importamos User para la comprobación inicial de admin

from routes.auth import auth_bp

from routes.main import main_bp

from routes.admin import admin_bp

from sockets.chat_events import register_chat_events # Importamos la función para registrar eventos de chat

# Configuración del log para ver errores en consola

logging.basicConfig(level=logging.INFO)

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # Inicializar extensiones

    db.init_app(app)

    mail = Mail(app)

    # ¡Importante! Asegúrate de que socketio se inicialice con el objeto app

    socketio = SocketIO(app)

    # Adjuntar 'mail' a la app para que esté disponible en las rutas

    app.mail = mail

    # Registrar Blueprints (grupos de rutas)

    app.register_blueprint(auth_bp)

    app.register_blueprint(main_bp)

    app.register_blueprint(admin_bp)

    # Registrar eventos de SocketIO

    register_chat_events(socketio)

    # NO necesitamos una ruta /get_chat_key aquí

    # porque la clave la pasamos directamente en render_template en main.py

    return app, socketio

if __name__ == '__main__':

    app, socketio = create_app()

    with app.app_context():

        db.create_all() # Crea las tablas en la base de datos si no existen

        app.logger.info("Base de datos creada o actualizada.")

        # Puedes verificar si ya hay un admin.

        # Si no hay admins, el primer usuario que se registre será el admin.

        if User.query.filter_by(role='admin').first() is None:

            app.logger.warning("\n¡ATENCIÓN! No hay administradores registrados.")

            app.logger.warning("El PRIMER usuario que se registre será automáticamente asignado como administrador.")

            app.logger.warning("Asegúrate de registrarte tú primero para tener acceso de admin.\n")

    # Usar eventlet para un servidor de WebSockets más robusto

    # allow_unsafe_werkzeug=True solo para desarrollo

socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

import os

if os.environ.get("RENDER", "") == "true":

    from create_tables import *  # Ejecuta la creación de tablas al iniciar en Render