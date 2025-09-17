# 🤖 Tony — Asistente Administrativo con IA

Tony es un chatbot personalizado, desarrollado en Python con la API de OpenAI y Streamlit, que actúa como un asistente administrativo interno para responder consultas, procedimientos y otras tareas frecuentes en una organización.

---

## 🚀 Características

- Autenticación de usuarios (login por credenciales)
- Chat en tiempo real con almacenamiento de historial por usuario
- Asistente personalizado usando OpenAI Assistant API, ingestado con base de conocimiento símil RAG.
- Interfaz con diseño responsivo y limpio (custom CSS)
- Desplegable fácilmente en Streamlit Cloud

---

## 📁 Estructura del Proyecto

```
chatbot-tony/
├── app.py                     # Script principal de la aplicación
├── credentials.json           # Credenciales de acceso por usuario (ignorado en Git)
├── requirements.txt           # Dependencias del proyecto
├── .env.template              # Variables de entorno necesarias (sin claves reales)
├── assets/
│   └── style.css              # Estilos visuales personalizados
├── historial_*.json           # Archivos de historial por usuario (generados en tiempo de ejecución)
├── .gitignore                 # Archivos y carpetas excluidos del repo
```

---

## 🛠️ Instalación local

```bash
# Clonar el repositorio
git clone https://github.com/tuusuario/chatbot-tony.git
cd chatbot-tony

# Crear y activar entorno virtual (opcional pero recomendado)
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env desde plantilla
cp .env.template .env
```

---

## 🧪 Ejecución

```bash
streamlit run app.py
```

> Asegurate de tener configuradas las variables en `.env`:
>
> ```
> OPENAI_API_KEY=sk-...
> ASSISTANT_ID=asst_...
> ```

Y de contar con un archivo `credentials.json` con el siguiente formato:

```json
{
  "usuario1": "clave1",
  "usuario2": "clave2"
}
```

---

## ☁️ Deploy en Streamlit Cloud

1. Subí este repo a GitHub
2. Ingresá a [streamlit.io/cloud](https://streamlit.io/cloud)
3. Seleccioná el repo
4. Confirmá que el archivo de entrada sea `app.py`
5. Agregá las variables de entorno necesarias en el panel de configuración (`OPENAI_API_KEY`, `ASSISTANT_ID`)

---

## 🧑‍💻 Autor

Desarrollado por [Federico Colombo](https://www.linkedin.com/in/fedecolombo/) como asistente interno de IA con conocimiento símil RAG.
Proyecto modular y escalable.