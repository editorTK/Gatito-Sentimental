# 🐱 Gatito Sentimental

**Gatito Sentimental** es una pequeña aplicación web en desarollador hecha con Flask. Por el momento,  Incluye autenticación, verificación por correo electrónico, roles de usuario, seguridad básica contra bots, y un panel administrativo. 


---

## 🌐 Funcionalidades principales

- ✔️ Registro con verificación de correo (enlace con token)
- 🔐 Inicio de sesión con control de intentos fallidos
- 🛡️ Protección básica contra bots y ataques de fuerza bruta
- 💬 Chat para usuarios registrados y confirmados
- 🧑‍💼 Panel de administración para gestionar usuarios y roles
- 💌 Envío de correos con Flask-Mail
- 🧠 Estructura basada en Blueprints para escalabilidad

---
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
