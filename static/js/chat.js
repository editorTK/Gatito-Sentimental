
// static/js/chat.js

const socket = io();
const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const currentUsername = "{{ session.username }}"; // Esta línea será interpretada por Jinja2 en el HTML

// Simulamos URLs de perfil para pruebas (ajustar en el backend si se tienen reales)
const profilePics = [
    "https://picsum.photos/id/1005/50/50",
    "https://picsum.photos/id/1011/50/50",
    "https://picsum.photos/id/1012/50/50",
    "https://picsum.photos/id/1015/50/50",
    "https://picsum.photos/id/1018/50/50",
    "https://picsum.photos/id/1025/50/50",
];
function getProfilePicUrl(username) {
    // Esto es solo un placeholder, en un proyecto real la URL de la imagen vendría del servidor
    // podrías tener una lógica para asignar imágenes de perfil basadas en el username o ID del usuario.
    // Por ahora, usamos un hash simple para obtener una imagen "aleatoria" consistente.
    let hash = 0;
    for (let i = 0; i < username.length; i++) {
        hash = username.charCodeAt(i) + ((hash << 5) - hash);
    }
    const index = Math.abs(hash % profilePics.length);
    return profilePics[index];
}

// Lógica para el menú de usuario (adaptado a las nuevas clases)
const userMenuToggle = document.getElementById('user-menu-toggle');
const userMenu = document.getElementById('user-menu');

userMenuToggle.addEventListener('click', function(event) {
    event.stopPropagation(); // Evitar que el clic en el botón cierre el menú inmediatamente
    userMenu.classList.toggle('hidden');
});

// Cerrar el menú si se hace clic fuera de él
window.addEventListener('click', function(e) {
    if (!userMenuToggle.contains(e.target) && !userMenu.contains(e.target)) {
        userMenu.classList.add('hidden');
    }
});

socket.on('connect', function() {
    socket.emit('join', { username: currentUsername });
});

socket.on('message', function(data) {
    const senderUsername = data.sender_username;
    const messageText = data.message;
    
    const isSent = senderUsername === currentUsername;

    const messageWrapper = document.createElement('div');
    messageWrapper.classList.add('flex', 'items-end', 'gap-3', 'p-2');
    if (isSent) {
        messageWrapper.classList.add('justify-end');
    }

    const bubbleContent = document.createElement('div');
    bubbleContent.classList.add('flex', 'flex-1', 'flex-col', 'gap-1');
    if (isSent) {
        bubbleContent.classList.add('items-end');
    } else {
        bubbleContent.classList.add('items-start');
    }

    const usernameElement = document.createElement('p');
    usernameElement.classList.add('text-[#9daebe]', 'text-[13px]', 'font-normal', 'leading-normal', 'max-w-[360px]');
    if (isSent) {
        usernameElement.classList.add('text-right');
    }
    usernameElement.textContent = senderUsername;

    const messageElement = document.createElement('p');
    messageElement.classList.add('text-base', 'font-normal', 'leading-normal', 'flex', 'max-w-[360px]', 'rounded-xl', 'px-4', 'py-3');
    if (isSent) {
        messageElement.classList.add('bg-[#dce8f3]', 'text-[#141a1f]');
    } else {
        messageElement.classList.add('bg-[#2b3640]', 'text-white');
    }
    messageElement.textContent = messageText;

    const profilePicDiv = document.createElement('div');
    profilePicDiv.classList.add('bg-center', 'bg-no-repeat', 'aspect-square', 'bg-cover', 'rounded-full', 'w-8', 'h-8', 'shrink-0');
    profilePicDiv.style.backgroundImage = `url('${getProfilePicUrl(senderUsername)}')`;

    bubbleContent.appendChild(usernameElement);
    bubbleContent.appendChild(messageElement);

    if (isSent) {
        messageWrapper.appendChild(bubbleContent);
        messageWrapper.appendChild(profilePicDiv);
    } else {
        messageWrapper.appendChild(profilePicDiv);
        messageWrapper.appendChild(bubbleContent);
    }

    chatBox.appendChild(messageWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
});

socket.on('error_message', function(data) {
    alert(data.msg);
    window.location.href = '/';
});

sendButton.addEventListener('click', function() {
    const message = messageInput.value.trim();
    if (message) {
        socket.emit('send_message', { message: message, sender_username: currentUsername });
        messageInput.value = '';
    }
});

messageInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendButton.click();
    }
});

window.onbeforeunload = function() {
    socket.emit('leave', { username: currentUsername });
    socket.disconnect();
};

