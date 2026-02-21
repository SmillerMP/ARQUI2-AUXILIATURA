//  CONFIGURACIÓN MQTT
// Usar ruta relativa que nginx redirigirá al broker
// Detecta automáticamente si usar WS o WSS según el protocolo de la página
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const broker = `${wsProtocol}//${window.location.host}/mqtt`;
const options = {
    username: "smillermp",
    password: "arqui2",
    clientId: "webchat-" + Math.random().toString(16).substr(2, 8)
};
const TOPIC_CHAT = "chat/messages"; // Topic para el chat

//  VARIABLES GLOBALES
let client = null;
let isConnected = false;

//  REFERENCIAS DOM
const statusIndicator = document.getElementById('statusIndicator');
const connectionStatus = document.getElementById('connectionStatus');
const chatArea = document.getElementById('chatArea');
const messageInput = document.getElementById('messageInput');
const btnSend = document.getElementById('btnSend');

//  FUNCIONES DE INTERFAZ

/**
 * Agrega un mensaje al área de chat
 * @param {string} text - Texto del mensaje
 * @param {string} type - Tipo de mensaje: 'received', 'sent', 'system'
 * @param {boolean} showTime - Mostrar timestamp
 */
function addMessage(text, type = 'received', sender = '', showTime = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';

    if (sender && type !== 'system') {
        const senderName = document.createElement('div');
        senderName.className = 'message-sender';
        senderName.textContent = sender;
        bubble.appendChild(senderName);
    }

    const messageText = document.createElement('p');
    messageText.className = 'message-text';
    messageText.textContent = text;
    bubble.appendChild(messageText);

    if (showTime && type !== 'system') {
        const time = document.createElement('span');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        bubble.appendChild(time);
    }

    messageDiv.appendChild(bubble);
    chatArea.appendChild(messageDiv);

    // Scroll automático al último mensaje
    chatArea.scrollTop = chatArea.scrollHeight;

    // Limpiar el empty state si existe
    const emptyState = chatArea.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
}

/**
 * Actualiza el estado visual de la conexión
 * @param {boolean} connected - Estado de la conexión
 */
function updateConnectionStatus(connected) {
    isConnected = connected;

    if (connected) {
        statusIndicator.classList.add('connected');
        connectionStatus.textContent = 'Conectado';
        messageInput.disabled = false;
        btnSend.disabled = false;
        addMessage('Conectado al chat', 'system', false);
    } else {
        statusIndicator.classList.remove('connected');
        connectionStatus.textContent = 'Desconectado';
        messageInput.disabled = true;
        btnSend.disabled = true;
        addMessage('Desconectado del servidor', 'system', false);
    }
}

//  FUNCIONES MQTT

/**
 * Envía un mensaje a través de MQTT
 */
function sendMessage() {
    const message = messageInput.value.trim();

    if (!message || !isConnected) {
        return;
    }

    try {
        // Publicar mensaje en el topic
        client.publish(TOPIC_CHAT, JSON.stringify({
            sender: options.clientId,
            message: message
        }));

        // Extraer solo los últimos 4 caracteres del ID para hacerlo más corto
        const shortId = options.clientId.split('-').pop().substring(0, 4);

        // Agregar mensaje al chat como enviado
        addMessage(message, 'sent', `Tú`);

        // Limpiar input
        messageInput.value = '';
        messageInput.focus();
    } catch (error) {
        addMessage('Error enviando mensaje: ' + error.message, 'system', false);
    }
}

/**
 * Conecta al broker MQTT y configura los callbacks
 */
function connectMQTT() {
    try {
        // Crear cliente MQTT
        client = mqtt.connect(broker, options);

        // Evento: Conexión exitosa
        client.on("connect", () => {
            console.log("Conectado al broker MQTT");
            updateConnectionStatus(true);

            // Suscribirse al topic de chat
            client.subscribe(TOPIC_CHAT, (err) => {
                if (err) {
                    console.error("Error suscribiéndose:", err);
                    addMessage('Error al suscribirse al chat', 'system', false);
                } else {
                    console.log(`Suscrito a ${TOPIC_CHAT}`);
                }
            });
        });

        // Evento: Mensaje recibido
        client.on("message", (topic, message) => {
            if (topic === TOPIC_CHAT) {
                try {
                    const payload = JSON.parse(message.toString());
                    const sender = payload.sender || 'Anónimo';
                    const text = payload.message;
                    
                    // Extraer solo los últimos 4 caracteres del ID para hacerlo más corto
                    const shortId = sender.split('-').pop().substring(0, 4);

                    // Solo mostrar como recibido si no es igual al último mensaje enviado
                    const lastMessage = chatArea.lastElementChild;
                    const isSentMessage = lastMessage &&
                        lastMessage.classList.contains('message-sent') &&
                        lastMessage.querySelector('.message-text').textContent === text;

                    if (!isSentMessage) {
                        addMessage(text, 'received', `Usuario-${shortId}`);
                    }
                } catch (error) {
                    console.error('Error parseando mensaje:', error);
                    // Si no es JSON, mostrar el mensaje tal cual
                    addMessage(message.toString(), 'received');
                }
            }
        });

        // Evento: Error
        client.on("error", (error) => {
            console.error("Error MQTT:", error);
            updateConnectionStatus(false);
        });

        // Evento: Conexión cerrada
        client.on("close", () => {
            console.log("Conexión MQTT cerrada");
            updateConnectionStatus(false);
        });

        // Evento: Cliente offline
        client.on("offline", () => {
            console.log("Cliente MQTT offline");
            updateConnectionStatus(false);
        });

    } catch (error) {
        console.error("Error inicializando MQTT:", error);
        addMessage('Error de conexión: ' + error.message, 'system', false);
        updateConnectionStatus(false);
    }
}

//  EVENT LISTENERS

// Permitir enviar con Enter
messageInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', function () {
    connectMQTT();
});

// Manejar cierre de ventana
window.addEventListener('beforeunload', function () {
    if (client && isConnected) {
        client.end();
    }
});
