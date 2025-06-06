# 🐱 Gatito Sentimental

**Gatito Sentimental** es una aplicación web de ejemplo desarrollada con el framework Flask. Su objetivo es mostrar una implementación sencilla de un sistema de chat con autenticación, confirmación de correo electrónico y gestión de usuarios a través de un panel de administración. El proyecto se encuentra en desarrollo, aunque ya ofrece todas las funcionalidades básicas para experimentar o aprender.


---

## 🌐 Funcionalidades principales

- ✔️ Registro de usuarios con verificación de correo (enlace con token).
- 🔐 Inicio de sesión protegido con control de intentos fallidos.
- 🛡️ Medidas elementales contra bots y ataques de fuerza bruta.
- 💬 Chat disponible para usuarios autenticados y confirmados.
- 🧑‍💼 Panel para administrar usuarios y asignar roles.
- 💌 Envío de notificaciones por correo mediante Flask-Mail.
- 🧠 Estructura modular basada en Blueprints que facilita la escalabilidad.

---

## 📋 Requisitos previos

- Python 3.10 o superior
- Acceso a un servidor SMTP para el envío de correos
- Opcionalmente una base de datos PostgreSQL

## 🔧 Instalación

1. Clonar este repositorio
2. Crear y activar un entorno virtual
3. Instalar las dependencias con `pip install -r requirements.txt`
4. Configurar las variables de entorno necesarias (ver sección siguiente)

## ▶️ Ejecución

Para desarrollo local se puede lanzar directamente:

```bash
python app.py
```

En producción se recomienda usar un servidor WSGI como Gunicorn:

```bash
gunicorn wsgi:app
```

## ⚙️ Configuración

Las principales variables de entorno son:

- `FLASK_SECRET_KEY`: clave secreta para Flask
- `DATABASE_URL`: URL de la base de datos (por defecto SQLite)
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`: datos para el servidor de correo
- `LOGIN_ATTEMPTS_LIMIT` y `LOCKOUT_DURATION_MINUTES`: parámetros de seguridad

---

## 📂 Detalle por archivo

### 🔹 `app.py`
- Crea la app Flask, configura los Blueprints, carga la configuración.
- Inicia extensiones como SQLAlchemy, Mail y SocketIO.
- Arranca el servidor.

### 🔹 `config.py`
- Variables sensibles y configuraciones importantes:
  - `SECRET_KEY`
  - Parámetros de correo (SMTP)
  - Límites de intentos de login
  - Tiempo de bloqueo por fuerza bruta

### 🔹 `extensions.py`
- Centraliza la inicialización de extensiones Flask como:
  - `db` (SQLAlchemy)
  - `mail` (Flask-Mail)
  - `socketio` (Flask-SocketIO)

---

### 📚 `models.py`

Define los modelos de base de datos:

- `User`: incluye nombre de usuario, email, hash de contraseña, rol (admin/user), confirmación, intentos fallidos y bloqueo.
- `ConfirmationToken`: token para confirmar el correo electrónico, ligado a un usuario.

---

### 📦 `routes/`

#### `auth.py`
- `register`: registra usuarios, verifica datos, crea tokens de confirmación.
- `login`: gestiona el inicio de sesión con protección contra ataques.
- `logout`: limpia la sesión del usuario.
- `confirm_email`: activa la cuenta usando un enlace enviado por correo.

#### `main.py`
- `index`: muestra el formulario de login/registro.
- `chat`: acceso al chat si el usuario está logueado y confirmado.

#### `admin.py`
- `manage_users`: página de administración para ver todos los usuarios.
- `set_user_role`: cambiar el rol (admin/user) de un usuario.

---

### 🎨 `templates/`

- `index.html`: página con formularios de login y registro.
- `chat.html`: interfaz principal del chat (¡el corazón sentimental!).
- `manage_users.html`: tabla de usuarios con botones para cambiar roles.

---

### 🛠️ `utilities.py`

- Decoradores personalizados:
  - `@login_required`: protege rutas privadas.
  - `@admin_required`: permite acceso solo a administradores.

---

## 🤝 Contribuciones

Las contribuciones y sugerencias son bienvenidas. Puedes abrir un issue o enviar un pull request si deseas mejorar el proyecto.
