"""
Fixi WebSocket chat — respuestas IA (Groq) con fallback FAQ local.
"""

import os
from groq import Groq
from flask_socketio import emit

# ---------------------------------------------------------------------------
# Configuración Groq
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = (
    "Eres Fixi, el asistente virtual de HogarFix, una plataforma web colombiana "
    "para conectar clientes con técnicos independientes en Bogotá y Cundinamarca. "
    "Ayudas a los usuarios con: registro e inicio de sesión (incluyendo Google), "
    "reservar y cancelar servicios, información sobre técnicos y verificación, "
    "precios y tarifas, seguridad de la plataforma, recuperación de contraseñas, "
    "calificaciones y reseñas, disponibilidad y horarios, y notificaciones.\n"
    "REGLAS OBLIGATORIAS:\n"
    "1. Ortografía perfecta en español: tildes (á é í ó ú ñ), signos de apertura (¿ ¡) y cierre (? !).\n"
    "2. Mayúscula solo al inicio de oración y en nombres propios.\n"
    "3. FORMATO de respuesta: cuando la respuesta tiene varios pasos o puntos, "
    "sepáralos con saltos de línea (\\n) y usa viñetas con el guion (- ) al inicio de cada punto. "
    "Ejemplo:\nPara reservar un servicio:\n- Busca un técnico en la sección de búsqueda.\n"
    "- Selecciona fecha y hora disponibles.\n- Confirma la reserva.\n"
    "4. Máximo 4 puntos por respuesta. Si la respuesta es simple, escríbela en una sola oración.\n"
    "5. Si la pregunta no es sobre HogarFix, indícalo brevemente y ofrece los temas que cubres.\n"
    "6. Nunca inventes precios específicos ni políticas que no conozcas."
)

_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        _groq_client = Groq(api_key=api_key)
        return _groq_client
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Base de conocimiento de Fixi
# ---------------------------------------------------------------------------
_FAQ = [
    {
        "keywords": ["registro", "registrar", "crear cuenta", "cuenta nueva"],
        "response": (
            "¡Claro! Para registrarte en HogarFix haz clic en 'Crear cuenta' y "
            "completa tus datos. Puedes registrarte como cliente o como técnico. "
            "¿Te gustaría que te guíe paso a paso?"
        ),
    },
    {
        "keywords": ["reserva", "reservar", "cita", "agendar", "solicitar servicio"],
        "response": (
            "Para reservar: busca un técnico, elige el servicio y la localidad, "
            "luego selecciona fecha y hora disponibles. ¡En menos de 2 minutos!"
        ),
    },
    {
        "keywords": ["cancelar", "cancelacion", "anular"],
        "response": (
            "Puedes cancelar una reserva desde tu historial de reservas. "
            "Sin penalización hasta 24 horas antes del servicio."
        ),
    },
    {
        "keywords": ["precio", "costo", "cuanto cobra", "cuánto cobra", "tarifa", "cobro", "pago"],
        "response": (
            "El precio varía según el técnico, el servicio y la localidad. "
            "Puedes ver el precio estimado al seleccionar cada técnico en la búsqueda."
        ),
    },
    {
        "keywords": ["tecnico", "ser tecnico", "quiero ser tecnico", "publicar trabajo"],
        "response": (
            "¡Genial! Para ser técnico en HogarFix regístrate con la opción 'Técnico', "
            "completa tu perfil con documentos y especialidades, y espera la "
            "verificación en 24-48 horas hábiles."
        ),
    },
    {
        "keywords": ["seguridad", "seguro", "proteccion", "protección", "privacidad", "datos"],
        "response": (
            "Tu información está protegida con cifrado HTTPS, contraseñas con hash "
            "y verificación en dos pasos (OTP). Nunca vendemos tus datos a terceros."
        ),
    },
    {
        "keywords": ["contraseña", "contrasena", "password", "olvide", "olvidé", "recuperar"],
        "response": (
            "Haz clic en '¿Olvidaste tu contraseña?' en el login. "
            "Te enviaremos un enlace seguro a tu correo para restablecerla."
        ),
    },
    {
        "keywords": ["verificacion", "verificación", "verificado", "cedula", "documento", "identidad"],
        "response": (
            "La verificación requiere foto de tu cédula (frente y reverso) y una selfie. "
            "El equipo HogarFix revisa en 24-48 horas hábiles."
        ),
    },
    {
        "keywords": ["soporte", "ayuda", "problema", "error", "contacto"],
        "response": (
            "Para soporte escríbenos a soporte@hogarfix.co. "
            "Respondemos en menos de 24 horas hábiles."
        ),
    },
    {
        "keywords": ["disponibilidad", "horario", "horas", "cuando"],
        "response": (
            "Cada técnico configura su disponibilidad en su perfil. "
            "Puedes ver los horarios disponibles al seleccionarlo en la búsqueda."
        ),
    },
    {
        "keywords": ["calificacion", "calificación", "estrella", "resena", "reseña", "review"],
        "response": (
            "Después de cada servicio puedes dejar una calificación y reseña al técnico. "
            "Esto ayuda a la comunidad a elegir mejor."
        ),
    },
    {
        "keywords": ["google", "microsoft", "iniciar sesion", "iniciar sesión", "login", "acceso"],
        "response": (
            "Puedes iniciar sesión con tu correo y contraseña, "
            "o usando tu cuenta de Google. ¡Rápido y seguro!"
        ),
    },
    {
        "keywords": ["foto", "perfil", "imagen", "avatar"],
        "response": (
            "Puedes subir o cambiar tu foto de perfil desde la sección 'Perfil' "
            "en tu panel. Formatos aceptados: JPG, PNG."
        ),
    },
    {
        "keywords": ["notificacion", "notificación", "aviso", "correo", "email"],
        "response": (
            "Las notificaciones llegan a tu correo y también aparecen en el "
            "ícono de campana en la barra superior de la app."
        ),
    },
]

_DEFAULT = (
    "¡Gracias por escribir! Puedo ayudarte con registro, reservas, técnicos, "
    "precios y seguridad. ¿Sobre qué tema tienes dudas?"
)


def _get_response(text: str) -> str:
    msg = text.strip()
    if not msg:
        return _DEFAULT

    # Intentar respuesta con Groq IA
    client = _get_groq_client()
    if client:
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": msg},
                ],
                max_tokens=200,
                temperature=0.4,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Fixi][Groq ERROR] {type(e).__name__}: {e}")
    else:
        print(f"[Fixi] Sin cliente Groq — KEY cargada: {bool(os.environ.get('GROQ_API_KEY', '').strip())}")

    # Fallback: FAQ local por palabras clave
    msg_lower = msg.lower()
    for faq in _FAQ:
        for keyword in faq["keywords"]:
            if keyword in msg_lower:
                return faq["response"]
    return _DEFAULT


# ---------------------------------------------------------------------------
# Registro de eventos Socket.IO
# ---------------------------------------------------------------------------

def register_socketio_events(socketio):
    @socketio.on("fixi_message")
    def handle_fixi_message(data):
        msg = (data or {}).get("message", "").strip() if isinstance(data, dict) else ""
        response = _get_response(msg)
        emit("fixi_response", {"message": response})
