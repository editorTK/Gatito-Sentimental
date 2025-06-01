
from flask import session
from flask_socketio import emit, join_room, leave_room
from utilities import login_required # Importamos el decorador

# Este decorador custom para SocketIO no es como los de Flask HTTP.
# Necesitamos asegurar que session esté disponible para SocketIO
# Flask-SocketIO maneja esto automáticamente si la sesión de Flask está configurada.

def register_chat_events(socketio):
    @socketio.on('join')
    @login_required
    def handle_join(data):
        username = session.get('username')
        email_confirmed = session.get('email_confirmed')
        if not username or not email_confirmed:
            emit('error_message', {'msg': 'Necesitas iniciar sesión y confirmar tu correo para chatear.'})
            return
        room = 'general_chat'
        join_room(room)
        emit('message', {'msg': f'**{username}** ha entrado al chat.'}, room=room)
        print(f'{username} se unió a la sala {room}')

    @socketio.on('leave')
    @login_required
    def handle_leave(data):
        username = session.get('username')
        if not username: return
        room = 'general_chat'
        leave_room(room)
        emit('message', {'msg': f'**{username}** ha salido del chat.'}, room=room)
        print(f'{username} salió de la sala {room}')

    @socketio.on('send_message')
    @login_required
    def handle_message(data):
        username = session.get('username')
        if not username: return
        message = data['message']
        room = 'general_chat'
        emit('message', {'msg': f'**{username}**: {message}'}, room=room)
        print(f'Mensaje de {username}: {message}')
