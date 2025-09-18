import streamlit as st
import openai
import os
import time
import json
from dotenv import load_dotenv

# --- Configuración de Autenticación ---
if os.getenv("CREDENTIALS_JSON"):
    # Si está definida como variable de entorno (ej. en Streamlit Cloud)
    CREDENTIALS = json.loads(os.getenv("CREDENTIALS_JSON"))
else:
    # Si estás trabajando en local, leé desde el archivo
    with open("credentials.json", "r") as f:
        CREDENTIALS = json.load(f)

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Configurar la página
st.set_page_config(page_title="Tony", page_icon="🧑‍💻")

# Cargar CSS externo
def load_css(file_path):
    with open(file_path) as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

# Función para extraer texto robusto del mensaje
def extract_message_text(msg):
    """
    Extrae texto robustamente desde diferentes formatos del mensaje,
    compatible con objetos OpenAI AssistantMessage y dicts.
    """
    try:
        # Caso 1: objeto OpenAI con .content (lista de bloques)
        if hasattr(msg, "content"):
            blocks = msg.content
            if isinstance(blocks, list):
                texts = []
                for block in blocks:
                    if hasattr(block, "text"):
                        texts.append(block.text.value)
                return "\n\n".join(texts)
            return str(blocks)

        # Caso 2: mensaje como dict tradicional
        elif isinstance(msg, dict):
            content = msg.get("content", "")
            if isinstance(content, list):
                texts = []
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        texts.append(part["text"]["value"])
                return "\n\n".join(texts)
            return str(content)

        return "[Mensaje vacío]"
    
    except Exception as e:
        return f"[Error al leer mensaje: {e}]"

# Función para guardar el historial de chat
def save_history(username):
    """
    Guarda solo contenido serializable del historial para evitar errores.
    """
    cleaned_messages = []

    for msg in st.session_state.messages:
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", "assistant")
        
        try:
            if isinstance(msg, dict):
                content = msg.get("content", "")
            else:
                # Objeto complejo → convertir a string plano
                content = extract_message_text(msg)
        except Exception as e:
            content = f"[Error al convertir contenido: {e}]"

        # Forzar contenido a string final
        cleaned_messages.append({
            "role": str(role),
            "content": str(content)
        })

    # Guardar en JSON solo texto puro
    with open(f"historial_{username}.json", "w") as f:
        json.dump(cleaned_messages, f)

def load_history(username):
    """
    Carga el historial del usuario desde archivo JSON.
    Si el archivo no existe o está corrupto, inicializa vacío.
    """
    try:
        path = f"historial_{username}.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                st.session_state.messages = json.load(f)
        else:
            st.session_state.messages = []
    except Exception as e:
        st.warning(f"No se pudo cargar el historial: {e}")
        st.session_state.messages = []

# ----------------- INICIO DE LA APLICACIÓN -----------------

# Inicializar el estado de autenticación si no existe
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None

# Mostrar el formulario de inicio de sesión si no está autenticado
if not st.session_state.authenticated:
    st.title("🔐 Acceso a Tony")

    st.markdown("Por favor, ingresa tus credenciales.")

    username_input = st.text_input("Usuario", key="username_input")
    password_input = st.text_input("Contraseña", type="password", key="password_input")

    login_button = st.button("Iniciar sesión")

    if login_button:
        if username_input in CREDENTIALS and CREDENTIALS[username_input] == password_input:
            st.session_state.authenticated = True
            st.session_state.username = username_input
            st.success("¡Acceso concedido! Recargando la página...")
            st.rerun() 
        else:
            st.error("Credenciales incorrectas. Por favor, intenta de nuevo.")

# Si el usuario está autenticado, muestra la aplicación principal
else:
    load_css("assets/style.css")

    st.markdown("<div class='header-container'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>🧑‍💻 Tony</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Asistente administrativo.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div class='header-spacer'></div>", unsafe_allow_html=True)

    if "messages" not in st.session_state or st.session_state.username != st.session_state.get("last_username"):
        load_history(st.session_state.username)
        st.session_state.last_username = st.session_state.username

    if "thread_id" not in st.session_state:
        thread = openai.beta.threads.create()
        st.session_state.thread_id = thread.id

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(extract_message_text(msg), unsafe_allow_html=True)

    if user_input := st.chat_input("Escribí tu consulta..."):
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(extract_message_text({"content": user_input}), unsafe_allow_html=True)

        save_history(st.session_state.username)

        with st.spinner("Tony está pensando 💡..."):
            openai.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=user_input
            )

            run = openai.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=ASSISTANT_ID
            )

            while True:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                time.sleep(1)

            # Obtener la última respuesta del asistente
            messages = openai.beta.threads.messages.list(thread_id=st.session_state.thread_id)
            ai_response = extract_message_text(messages.data[0])  # ← usa la función robusta

        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        with st.chat_message("assistant"):
            st.markdown(extract_message_text({"content": ai_response}), unsafe_allow_html=True)

        save_history(st.session_state.username)

    st.markdown("<div class='footer'>Creado con 🚀 por Fede. Asistente personal de IA.</div>", unsafe_allow_html=True)