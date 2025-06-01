# config.py
import os
import datetime
# Importamos load_dotenv para cargar las variables del archivo .env
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
load_dotenv()
# --- VERIFICACIÓN TEMPORAL (BORRAR DESPUÉS) ---
print("--- Verificando variables de entorno ---")
print(f"FLASK_SECRET_KEY: {os.getenv('FLASK_SECRET_KEY') is not None}")
print(f"MAIL_USERNAME: {os.getenv('MAIL_USERNAME')}")
print(f"MAIL_PASSWORD (cargado?): {os.getenv('MAIL_PASSWORD') is not None}")
print(f"MAIL_SERVER: {os.getenv('MAIL_SERVER')}")
print(f"MAIL_PORT: {os.getenv('MAIL_PORT')}")
print(f"MAIL_USE_TLS: {os.getenv('MAIL_USE_TLS')}")
print(f"MAIL_USE_SSL: {os.getenv('MAIL_USE_SSL')}")
print("---------------------------------------")
# --------------------------------------------

class Config:
    # Clave Secreta para la sesión de Flask
    # Usa os.getenv() para leer la variable de entorno FLASK_SECRET_KEY
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY') or os.urandom(24) # Fallback para si no está definida

    # Configuración de la base de datos SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de Flask-Mail para envío de correos
    # Leemos directamente de las variables de entorno
    MAIL_SERVER = os.getenv('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') or 'tu_correo@gmail.com'
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') or 'tu_contraseña_de_aplicacion'
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER') or 'tu_correo@gmail.com'

    # --- Configuración para protección contra fuerza bruta ---
    LOGIN_ATTEMPTS_LIMIT = int(os.getenv('LOGIN_ATTEMPTS_LIMIT') or 5)
    LOCKOUT_DURATION_MINUTES = int(os.getenv('LOCKOUT_DURATION_MINUTES') or 10)
