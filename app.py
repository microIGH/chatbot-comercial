from flask import Flask, request, jsonify, render_template_string
import anthropic
import os
import json
from datetime import datetime
import hashlib

app = Flask(__name__)

# Configuración
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None

# Almacenamiento temporal en memoria (después migrar a base de datos)
conversaciones = {}

# Configuraciones por tipo de negocio
CONFIGURACIONES = {
    "restaurante": {
        "mensaje_bienvenida": "¡Hola! Soy el asistente virtual de nuestro restaurante. ¿En qué puedo ayudarte hoy?",
        "contexto": "Eres el asistente de un restaurante. Ayuda con consultas sobre menú, horarios, reservaciones y pedidos.",
        "intenciones": ["menu", "horarios", "reservaciones", "pedidos", "ubicacion"]
    },
    "ecommerce": {
        "mensaje_bienvenida": "¡Bienvenido! ¿Buscas algún producto específico o necesitas ayuda?",
        "contexto": "Eres el asistente de una tienda online. Ayuda con productos, inventario, compras y envíos.",
        "intenciones": ["productos", "stock", "compras", "envios", "devoluciones"]
    },
    "general": {
        "mensaje_bienvenida": "¡Hola! ¿En qué puedo ayudarte hoy?",
        "contexto": "Eres un asistente virtual amigable y profesional.",
        "intenciones": ["informacion", "soporte", "consultas"]
    }
}

@app.route('/')
def home():
    return """
    <h1>Chatbot API - Funcionando ✅</h1>
    <p>Endpoints disponibles:</p>
    <ul>
        <li><code>/api/chat</code> - POST para enviar mensajes</li>
        <li><code>/widget.js</code> - JavaScript del widget</li>
        <li><code>/demo</code> - Demo del chatbot</li>
    </ul>
    """

@app.route('/widget.js')
def serve_widget():
    widget_js = """
// Widget de Chatbot - Integrable en cualquier sitio web
(function() {
    let chatConfig = {};
    let sessionId = '';
    let isOpen = false;

    // Función para inicializar el chatbot
    window.inicializarChatbot = function(config) {
        chatConfig = config;
        sessionId = generateSessionId();
        createWidget();
        loadStyles();
    };

    function generateSessionId() {
        return 'chat_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    function createWidget() {
        // Crear estructura HTML del widget
        const widgetHTML = `
            <div id="chatbot-widget" style="position: fixed; bottom: 20px; right: 20px; z-index: 10000;">
                <div id="chat-button" style="
                    width: 60px; height: 60px; border-radius: 50%; 
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white; display: flex; align-items: center; 
                    justify-content: center; cursor: pointer; font-size: 24px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    border: none; transition: transform 0.3s ease;
                ">💬</div>
                
                <div id="chat-window" style="
                    position: absolute; bottom: 70px; right: 0; width: 350px; height: 500px;
                    background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    display: none; flex-direction: column; overflow: hidden;
                ">
                    <div id="chat-header" style="
                        background: linear-gradient(45deg, #667eea, #764ba2);
                        color: white; padding: 15px; text-align: center; font-weight: bold;
                    ">Asistente Virtual</div>
                    
                    <div id="chat-messages" style="
                        flex: 1; padding: 15px; overflow-y: auto; background: #f8f9fa;
                    "></div>
                    
                    <div id="chat-input-container" style="
                        padding: 15px; background: white; border-top: 1px solid #e0e0e0;
                        display: flex; gap: 10px;
                    ">
                        <input id="chat-input" type="text" placeholder="Escribe tu mensaje..."
                            style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; outline: none;">
                        <button id="send-button" style="
                            background: #667eea; color: white; border: none; border-radius: 50%;
                            width: 40px; height: 40px; cursor: pointer;
                        ">➤</button>
                    </div>
                </div>
            </div>
        `;

        // Insertar en el DOM
        document.body.insertAdjacentHTML('beforeend', widgetHTML);

        // Event listeners
        document.getElementById('chat-button').onclick = toggleChat;
        document.getElementById('send-button').onclick = sendMessage;
        document.getElementById('chat-input').onkeypress = function(e) {
            if (e.key === 'Enter') sendMessage();
        };

        // Mensaje de bienvenida
        addMessage('bot', chatConfig.mensaje_bienvenida || '¡Hola! ¿En qué puedo ayudarte?');
    }

    function toggleChat() {
        const chatWindow = document.getElementById('chat-window');
        isOpen = !isOpen;
        chatWindow.style.display = isOpen ? 'flex' : 'none';
    }

    function sendMessage() {
        const input = document.getElementById('chat-input');
        const mensaje = input.value.trim();
        
        if (!mensaje) return;

        addMessage('user', mensaje);
        input.value = '';

        // Enviar a la API
        fetch(`${chatConfig.api_url || ''}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                mensaje: mensaje,
                session_id: sessionId,
                empresa_id: chatConfig.empresa_id || 'general',
                tipo_negocio: chatConfig.tipo_negocio || 'general'
            })
        })
        .then(response => response.json())
        .then(data => {
            addMessage('bot', data.respuesta || 'Lo siento, hubo un error.');
        })
        .catch(error => {
            addMessage('bot', 'Lo siento, no pude procesar tu mensaje. Intenta de nuevo.');
        });
    }

    function addMessage(tipo, texto) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageHTML = `
            <div style="margin-bottom: 15px; display: flex; ${tipo === 'user' ? 'justify-content: flex-end' : 'justify-content: flex-start'}">
                <div style="
                    max-width: 80%; padding: 10px 15px; border-radius: 18px; word-wrap: break-word;
                    ${tipo === 'user' ? 'background: #667eea; color: white;' : 'background: white; color: #333; border: 1px solid #e0e0e0;'}
                ">${texto}</div>
            </div>
        `;
        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
})();
    """
    return widget_js, 200, {'Content-Type': 'application/javascript'}

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    try:
        data = request.json
        mensaje = data.get('mensaje', '')
        session_id = data.get('session_id', '')
        empresa_id = data.get('empresa_id', 'general')
        tipo_negocio = data.get('tipo_negocio', 'general')

        if not mensaje:
            return jsonify({'error': 'Mensaje vacío'}), 400

        # Generar respuesta
        respuesta = generar_respuesta(mensaje, tipo_negocio, session_id)

        # Guardar conversación
        if session_id not in conversaciones:
            conversaciones[session_id] = []
        
        conversaciones[session_id].extend([
            {'tipo': 'user', 'mensaje': mensaje, 'timestamp': datetime.now().isoformat()},
            {'tipo': 'bot', 'mensaje': respuesta, 'timestamp': datetime.now().isoformat()}
        ])

        return jsonify({
            'respuesta': respuesta,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generar_respuesta(mensaje, tipo_negocio, session_id):
    # Si no hay Claude API, usar respuestas predefinidas
    if not client:
        return f"Echo: {mensaje} (Modo demo - configurar CLAUDE_API_KEY)"

    # Obtener configuración
    config = CONFIGURACIONES.get(tipo_negocio, CONFIGURACIONES['general'])
    
    # Obtener historial
    historial = conversaciones.get(session_id, [])
    contexto_historial = ""
    if historial:
        contexto_historial = "\\nHistorial de la conversación:\\n" + "\\n".join([
            f"{h['tipo']}: {h['mensaje']}" for h in historial[-6:]  # Últimos 6 mensajes
        ])

    # Crear prompt
    prompt = f"""
{config['contexto']}

{contexto_historial}

Usuario dice: {mensaje}

Responde de manera amigable, útil y profesional. Mantén la respuesta concisa (máximo 100 palabras).
"""

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return "Lo siento, estoy teniendo problemas técnicos. Por favor intenta de nuevo."

@app.route('/demo')
def demo():
    demo_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Demo Chatbot</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; }
        h1 { color: #333; text-align: center; }
        .demo-button { background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; margin: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Demo del Chatbot Comercial</h1>
        <p>Prueba diferentes configuraciones:</p>
        
        <button class="demo-button" onclick="initRestaurante()">Chatbot para Restaurante</button>
        <button class="demo-button" onclick="initEcommerce()">Chatbot para E-commerce</button>
        <button class="demo-button" onclick="initGeneral()">Chatbot General</button>
        
        <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px;">
            <h3>Instrucciones de Integración:</h3>
            <pre><code>&lt;script src="/widget.js"&gt;&lt;/script&gt;
&lt;script&gt;
  inicializarChatbot({
    empresa_id: "mi_empresa",
    tipo_negocio: "restaurante", // o "ecommerce", "general"
    api_url: window.location.origin
  });
&lt;/script&gt;</code></pre>
        </div>
    </div>

    <script src="/widget.js"></script>
    <script>
        function initRestaurante() {
            inicializarChatbot({
                empresa_id: "demo_restaurante",
                tipo_negocio: "restaurante",
                api_url: window.location.origin,
                mensaje_bienvenida: "¡Hola! Soy el asistente de nuestro restaurante. ¿Te ayudo con el menú o una reservación?"
            });
        }

        function initEcommerce() {
            inicializarChatbot({
                empresa_id: "demo_tienda",
                tipo_negocio: "ecommerce", 
                api_url: window.location.origin,
                mensaje_bienvenida: "¡Bienvenido a nuestra tienda! ¿Buscas algún producto específico?"
            });
        }

        function initGeneral() {
            inicializarChatbot({
                empresa_id: "demo_general",
                tipo_negocio: "general",
                api_url: window.location.origin
            });
        }
    </script>
</body>
</html>
    """
    return demo_html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
