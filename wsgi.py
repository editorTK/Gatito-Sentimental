from app import create_app

app, _ = create_app()  # ignoramos socketio porque Gunicorn solo necesita 'app'
