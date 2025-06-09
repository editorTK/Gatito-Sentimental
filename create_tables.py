from app import create_app
from models import db, User

app, _ = create_app()

with app.app_context():
    db.create_all()
    print("🎉 Tablas creadas.")
