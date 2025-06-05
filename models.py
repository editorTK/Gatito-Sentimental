# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import uuid
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')
    email_confirmed = db.Column(db.Boolean, default=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)

    # --- NUEVOS CAMPOS ---
    profile_picture_url = db.Column(db.String(255), nullable=True, default=None) # URL de la foto de perfil
    bio = db.Column(db.Text, nullable=True, default=None) # Biografía o descripción

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class ConfirmationToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now() + datetime.timedelta(hours=1))

    user = db.relationship('User', backref=db.backref('confirmation_tokens', lazy=True))

    def __repr__(self):
        return f'<ConfirmationToken {self.token}>'

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now() + datetime.timedelta(hours=1))

    user = db.relationship('User', backref=db.backref('password_reset_tokens', lazy=True))

    def __repr__(self):
        return f'<PasswordResetToken {self.token}>'
