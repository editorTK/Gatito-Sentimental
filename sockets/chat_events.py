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
            # Emitir un mensaje de error al cliente si no está logueado o email no confirmado
            emit('error_message', {'msg': 'Necesitas iniciar sesión y confirmar tu correo para chatear.'})
            return
        room = 'general_chat'
        join_room(room)
        # Cambiado 'msg' a 'message' para consistencia con el cliente que espera 'message'
        # y ahora es el campo principal del contenido del mensaje
        emit('message', {'sender_username': 'Sistema', 'message': f'{username} ha entrado al chat.'}, room=room)
        # print(f'{username} se unió a la sala {room}') # Comentado o eliminado

    @socketio.on('leave')
    @login_required
    def handle_leave(data):
        username = session.get('username')
        if not username: return
        room = 'general_chat'
        leave_room(room)
        # Cambiado 'msg' a 'message'
        emit('message', {'sender_username': 'Sistema', 'message': f'**{username}** ha salido del chat.'}, room=room)
        # print(f'{username} salió de la sala {room}') # Comentado o eliminado

    @socketio.on('send_message')
    @login_required
    def handle_message(data):
        username = session.get('username') # Nombre del usuario que envía el mensaje (desde la sesión)
        
        # *** AQUÍ ESTÁ EL CAMBIO CLAVE ***
        # Ahora el cliente envía el mensaje bajo la clave 'message', no 'encrypted_msg'
        message_content = data['message'] 
        # Opcional: El cliente envía 'sender_username', pero lo ignoramos y usamos el de la sesión para seguridad.
        # sender_username_from_client = data.get('sender_username') 

        if not username: 
            # Si por alguna razón la sesión se pierde aquí, emitir error.
            emit('error_message', {'msg': 'Tu sesión ha caducado. Por favor, inicia sesión de nuevo.'})
            return 

        room = 'general_chat'
        # Emitir el mensaje (ahora en texto plano) con el nombre de usuario del remitente
        # Usamos el username de la sesión para mayor seguridad y consistencia
        emit('message', {'sender_username': username, 'message': message_content}, room=room)
        # Ya no se imprime el mensaje en texto plano, puedes añadir un log aquí si quieres
        # print(f'Mensaje de {username}: {message_content}')
