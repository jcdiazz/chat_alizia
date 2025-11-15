import streamlit as st
import requests
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# Zona horaria de Lima, Perú
LIMA_TZ = ZoneInfo("America/Lima")

# Configuración de la página
st.set_page_config(
    page_title="Chat ALiZiA",
    page_icon="🤖",
    layout="centered"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
    <style>
    /* Ajustar el tamaño de la fuente general */
    .stMarkdown {
        font-size: 1.1rem;
    }
    
    /* Mejorar el espaciado del contenedor principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    
    /* Estilo para el input del chat */
    .stChatInput {
        border-radius: 20px;
    }
    
    /* Mejorar el espaciado de los mensajes */
    .stChatMessage {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Ocultar el botón de menú y footer de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Ajustar el tamaño del separador */
    hr {
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Configuración de la API de ALiZiA
API_ENDPOINT = "https://alizia-v4.calmdesert-4804d17b.eastus.azurecontainerapps.io/conversation"
API_HEADERS = {
    "Content-Type": "application/json",
    "token": "dev-chatpgt-token-xbpr435"
}

def call_api(message, session_id):
    """
    Función para llamar a la API de ALiZiA
    """
    try:
        # Configuración con session_id
        data = {
            "question": message,
            "session_id": session_id
        }

        response = requests.post(
            API_ENDPOINT,
            headers=API_HEADERS,
            json=data,
            timeout=90
        )

        if response.status_code == 200:
            result = response.json()
            # Extraer la respuesta
            answer = result.get("answer", "Sin respuesta disponible")

            return {
                "answer": answer,
                "raw_response": result
            }, None
        else:
            return f"Error API: {response.status_code} - {response.text}", "error"

    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {str(e)}", "error"
    except Exception as e:
        return f"Error inesperado: {str(e)}", "error"

# Inicializar el historial de chat y session_id
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"{datetime.now(LIMA_TZ).strftime('%Y%m%d%H%M%S')}"

# Logo centrado y más pequeño
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo_alizia.png", width=400)

st.markdown("<br>", unsafe_allow_html=True)

# Descripción con mejor formato y tamaño
st.markdown("""
<div style='text-align: center; font-size: 1.15rem; line-height: 1.8;'>
    <strong>¡Hola, Angello!</strong> Soy <strong>ALiZiA</strong>, tu aliada inteligente. 
    <br><br>
    Estoy aquí para ayudarte a obtener información clara y rápida sobre tus comercios, 
    transacciones, montos, abonos y comparativos.
    <br><br>
    <strong>Te entenderé a la perfección, así que pregúntame sin miedo.</strong> 
    Puedo buscar, analizar y mostrarte los datos en texto, tablas o gráficos, según lo necesites.
    <br><br>
    ¿Listo para comenzar, Angello? 😊
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# Contenedor para el chat
chat_container = st.container()

# Mostrar historial de mensajes
with chat_container:
    if len(st.session_state.messages) == 0:
        # Mensaje de bienvenida cuando no hay conversación
        st.markdown("""
        <div style='text-align: center; padding: 2rem; color: #666; font-size: 1.1rem;'>
            👋 ¡Empieza preguntándome lo que necesites!
        </div>
        """, unsafe_allow_html=True)
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f"<div style='font-size: 1.05rem;'>{message['content']}</div>", unsafe_allow_html=True)
            if message.get("timestamp"):
                st.caption(f"🕐 {message['timestamp']}")

# Input para nuevo mensaje
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # Agregar mensaje del usuario al historial
    timestamp = datetime.now(LIMA_TZ).strftime("%H:%M")
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": timestamp
    })
    
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(f"<div style='font-size: 1.05rem;'>{prompt}</div>", unsafe_allow_html=True)
        st.caption(f"🕐 {timestamp}")
    
    # Llamar a la API y mostrar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response_data, error = call_api(prompt, st.session_state.session_id)

            if error:
                st.error(response_data)
                response_text = "Lo siento, ocurrió un error al procesar tu mensaje."
                response_info = None
            else:
                response_text = response_data["answer"]
                response_info = response_data

            st.markdown(f"<div style='font-size: 1.05rem;'>{response_text}</div>", unsafe_allow_html=True)
            response_timestamp = datetime.now(LIMA_TZ).strftime("%H:%M")
            st.caption(f"🕐 {response_timestamp}")

            # Agregar respuesta del asistente al historial
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": response_timestamp,
                "metadata": response_info
            })
