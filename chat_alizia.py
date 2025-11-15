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
    layout="wide"
)

# Configuración de la API de ALiZiA
API_ENDPOINT = "https://dev-izi-chatbot-genai-api-v1-322392286721.us-central1.run.app/bloque2"
API_HEADERS = {
    "Content-Type": "application/json",
    "token": "dev-chatpgt-token-xbpr435"
}

def call_api(message, user_id="USER-00001", session_id=None):
    """
    Función para llamar a la API de Izipay
    """
    try:
        # Generar session_id único si no se proporciona
        if not session_id:
            session_id = f"{datetime.now(LIMA_TZ).strftime('%Y%m%d%H%M%S')}"

        # Configuración para datos de comercio
        base_config = {
            "question": message,
            "metadata": {
                "userId": user_id,
                "channelType": "Demo-Web",
                "sessionId": session_id
            },
            "configuration": {
                "business_case": "Chatbot de asesoria de Izipay",
                "prompt_params": {
                    "assistant_name": "IziBot",
                    "assistant_role": "Actúa como asistente virtual de Izipay.",
                    "company_name": "Izipay",
                    "company_activity": "Venta de servicios y terminales de puntos de venta llamados POS para la compra y venta.",
                    "conversation_purpose": "Atiende las consultas de los usuarios con entusiasmo y responde siempre de manera clara, breve y precisa. Tu misión principal es brindar soporte sobre todos los productos y servicios de Izipay, especialmente los terminales POS y cualquier otro servicio relacionado.\n- Tono: Siempre animado, profesional y directo.\n- Saludo del usuario: Si el usuario inicia con un saludo, no devuelvas el saludo. En lugar de eso, dile que puedes ayudarlo con sus preguntas sobre sus datos de comercio.\n- Preguntas ambiguas: Si la pregunta no está clara, pide detalles específicos para poder ofrecer una respuesta adecuada.\n- Límites: Si no puedes resolver algo, redirige al usuario con instrucciones claras para contactar al equipo de soporte humano."
                },
                "config_params": {
                    "maxMinutes": "None",
                    "temperature": 0.3,
                    "k_top_retrieval": 3
                },
                "knowledge_stores": ["dev_izipay_index_daco_azureopenai"]
            }
        }

        response = requests.post(
            API_ENDPOINT,
            headers=API_HEADERS,
            json=base_config,
            timeout=90
        )

        if response.status_code == 200:
            result = response.json()
            # Extraer la respuesta específica de Izipay
            answer = result.get("answer", "Sin respuesta disponible")

            # Información adicional que se puede mostrar
            trace = result.get("trace", "")
            trace_description = result.get("trace_description", "")
            satisfaction = result.get("satisfaction", "")
            transfer = result.get("transfer", "")
            finish = result.get("finish", "")
            citations = result.get("citations", [])

            return {
                "answer": answer,
                "trace": trace,
                "trace_description": trace_description,
                "citations": citations,
                "satisfaction": satisfaction,
                "transfer": transfer,
                "finish": finish,
                "raw_response": result
            }, None
        else:
            return f"Error API: {response.status_code} - {response.text}", "error"

    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {str(e)}", "error"
    except Exception as e:
        return f"Error inesperado: {str(e)}", "error"

# Inicializar el historial de chat y configuración
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"{datetime.now(LIMA_TZ).strftime('%Y%m%d%H%M%S')}"
if "user_id" not in st.session_state:
    st.session_state.user_id = f"USER-{datetime.now(LIMA_TZ).strftime('%Y%m%d%H%M%S')}"

# Título de la aplicación
#st.title("🤖 ALiZiA")
col_logo, col_space = st.columns([1, 3])
with col_logo:
    st.image("logo_alizia.png", width=300)

st.markdown("""
**¡Hola, Angello!** Soy **ALiZiA**, tu aliada inteligente. Estoy aquí para ayudarte a obtener información clara y rápida sobre tus comercios, transacciones, montos, abonos y comparativos.

No te preocupes por cómo preguntar: **te entenderé a la perfección, así que pregúntame sin miedo**. Puedo buscar, analizar y mostrarte los datos en texto, tablas o gráficos, según lo necesites.

¿Listo para comenzar, Angello? 😊
""")

st.divider()

# Sidebar con información
with st.sidebar:
    st.header("ALiZiA")

    # User ID con botón para generar nuevo
    st.write("User ID:")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.code(st.session_state.user_id, language=None)
    with col2:
        if st.button("🔄", key="refresh_user", help="Generar nuevo User ID"):
            st.session_state.user_id = f"USER-{datetime.now(LIMA_TZ).strftime('%Y%m%d%H%M%S')}"
            st.session_state.messages = []
            st.session_state.session_id = f"{datetime.now(LIMA_TZ).strftime('%Y%m%d%H%M%S')}"
            st.rerun()

    # Session ID con botón para generar nuevo
    st.write("Session ID:")
    col3, col4 = st.columns([4, 1])
    with col3:
        st.code(st.session_state.session_id, language=None)
    with col4:
        if st.button("🔄", key="refresh_session", help="Generar nuevo Session ID"):
            st.session_state.session_id = f"{datetime.now(LIMA_TZ).strftime('%Y%m%d%H%M%S')}"
            st.rerun()

    # Botón para limpiar el chat
    if st.button("🗑️ Limpiar Chat", use_container_width=True):
        st.session_state.messages = []
        # Generar nuevo session_id
        st.session_state.session_id = f"{datetime.now(LIMA_TZ).strftime('%Y%m%d%H%M%S')}"
        st.rerun()

# Contenedor para el chat
chat_container = st.container()

# Mostrar historial de mensajes
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
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
        st.markdown(prompt)
        st.caption(f"🕐 {timestamp}")
    
    # Llamar a la API y mostrar respuesta
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response_data, error = call_api(
                prompt, 
                st.session_state.user_id, 
                st.session_state.session_id
            )

            if error:
                st.error(response_data)
                response_text = "Lo siento, ocurrió un error al procesar tu mensaje."
                response_info = None
            else:
                response_text = response_data["answer"]
                response_info = response_data

            st.markdown(response_text)
            response_timestamp = datetime.now(LIMA_TZ).strftime("%H:%M")
            st.caption(f"🕐 {response_timestamp}")

            # Mostrar información adicional si está disponible
            if response_info and response_info.get("trace_description"):
                with st.expander("📋 Información adicional"):
                    if response_info.get("trace"):
                        st.write(f"**Traza:** {response_info['trace']}")
                    st.write(f"**Descripción de la traza:** {response_info['trace_description']}")
                    st.write(f"**Satisfacción:** {response_info['satisfaction']}")
                    st.write(f"**Transferir:** {response_info['transfer']}")
                    st.write(f"**Finalizar:** {response_info['finish']}")

                    # Mostrar citas si están disponibles
                    if response_info.get("citations"):
                        st.write("**Citas:**")
                        for i, citation in enumerate(response_info["citations"][:3]):  # Mostrar máximo 3 citas
                            option = citation.get("metadata", {}).get("option", "N/A")
                            st.write(f"- {option}")

            # Agregar respuesta del asistente al historial
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "timestamp": response_timestamp,
                "metadata": response_info
            })
