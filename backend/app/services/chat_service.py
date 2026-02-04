"""
Servicio de Chat RAG para DevRadar.
Arquitectura: Filtro de Intención (Groq) -> Historial (Redis) -> Búsqueda Semántica (Supabase) -> Respuesta (Groq).
"""
import os
import json
from typing import Optional
from dotenv import load_dotenv
from app.database import get_supabase
from app.embeddings import embed_text
from app.llm import GROQ_API_KEY

load_dotenv()

# Redis (opcional, fallback a memoria si no está disponible)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

# Cache en memoria como fallback si Redis no está disponible
_memory_cache: dict[str, list[dict]] = {}
MAX_HISTORY = 5
SIMILARITY_THRESHOLD = 0.27


def _get_redis_client():
    """Retorna cliente Redis o None si no está disponible."""
    if not REDIS_ENABLED:
        return None
    try:
        import redis
        return redis.from_url(REDIS_URL, decode_responses=True)
    except Exception as e:
        print(f"Redis no disponible, usando cache en memoria: {e}")
        return None


def _get_history(session_id: str) -> list[dict]:
    """Recupera los últimos MAX_HISTORY mensajes de la conversación."""
    redis_client = _get_redis_client()
    if redis_client:
        try:
            history_json = redis_client.lrange(f"chat:history:{session_id}", 0, MAX_HISTORY - 1)
            return [json.loads(msg) for msg in reversed(history_json)] if history_json else []
        except Exception as e:
            print(f"Error leyendo historial de Redis: {e}")
            return _memory_cache.get(session_id, [])[-MAX_HISTORY:]
    return _memory_cache.get(session_id, [])[-MAX_HISTORY:]


def _save_message(session_id: str, role: str, content: str):
    """Guarda un mensaje en el historial (Redis o memoria)."""
    msg = {"role": role, "content": content}
    redis_client = _get_redis_client()
    if redis_client:
        try:
            redis_client.lpush(f"chat:history:{session_id}", json.dumps(msg))
            redis_client.ltrim(f"chat:history:{session_id}", 0, MAX_HISTORY - 1)
            redis_client.expire(f"chat:history:{session_id}", 3600 * 24)  # 24 horas
        except Exception as e:
            print(f"Error guardando en Redis: {e}")
            if session_id not in _memory_cache:
                _memory_cache[session_id] = []
            _memory_cache[session_id].append(msg)
            _memory_cache[session_id] = _memory_cache[session_id][-MAX_HISTORY:]
    else:
        if session_id not in _memory_cache:
            _memory_cache[session_id] = []
        _memory_cache[session_id].append(msg)
        _memory_cache[session_id] = _memory_cache[session_id][-MAX_HISTORY:]


def _validar_intencion(mensaje: str) -> tuple[bool, Optional[str]]:
    """
    Filtro de Intención (Firewall): Valida si la pregunta es sobre mercado laboral, tecnología o consejos de carrera.
    Usa Groq llama-3.1-8b-instant para validación rápida.
    Retorna (True, None) si es válida; (False, mensaje_rechazo) si no lo es.
    """
    if not GROQ_API_KEY:
        return True, None

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            api_key=GROQ_API_KEY,
        )

        system = """Eres un filtro de intención para un chatbot de mercado laboral IT en Ecuador (DevRadar).

ACEPTA preguntas sobre:
- Mercado laboral IT (ofertas, salarios, demanda, tendencias)
- Tecnologías y herramientas (React, Python, etc.)
- Consejos de carrera profesional
- Búsqueda de trabajo en tecnología
- Comparaciones de tecnologías o roles

RECHAZA preguntas sobre:
- Temas no relacionados con tecnología o trabajo (deportes, cocina, entretenimiento, etc.)
- Consultas médicas, legales o financieras personales
- Chistes, conversación casual sin propósito profesional

Responde ÚNICAMENTE en JSON con estas claves:
- es_valida: true si la pregunta es válida; false si debe rechazarse.
- mensaje_rechazo: si es_valida es false, un mensaje amable explicando que solo respondemos sobre mercado laboral IT. Si es_valida es true, usa null.

Solo JSON, sin markdown."""

        human = f"""Valida esta pregunta del usuario:

"{mensaje}"

¿Es una pregunta válida sobre mercado laboral IT, tecnología o consejos de carrera? Responde solo con el JSON."""

        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=human)])
        text = response.content if hasattr(response, "content") else str(response)
        text = text.strip()

        if "```" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]
        data = json.loads(text)

        es_valida = data.get("es_valida", True)
        mensaje_rechazo = data.get("mensaje_rechazo") or "Lo siento, solo puedo responder preguntas sobre el mercado laboral IT, tecnologías y consejos de carrera profesional."

        return bool(es_valida), None if es_valida else mensaje_rechazo
    except Exception as e:
        print(f"Validación de intención falló: {e}")
        return True, None


def _buscar_ofertas_semanticas(query: str, limit: int = 5) -> list[dict]:
    """
    Búsqueda Semántica: Genera embedding del query y busca ofertas relevantes en Supabase.
    Retorna lista de ofertas (hasta 'limit').
    """
    try:
        query_embedding = embed_text(query)
        if not query_embedding:
            return []

        sb = get_supabase()

        # Intentar RPC match_jobs (retorna ofertas completas) o match_jobs_ids (retorna IDs)
        params = {
            "query_embedding": query_embedding,
            "match_threshold": SIMILARITY_THRESHOLD,
            "match_count": limit,
        }

        ofertas = []
        try:
            # Intentar match_jobs primero (si existe)
            rpc_response = sb.rpc("match_jobs", params).execute()
            if rpc_response.data:
                ofertas = rpc_response.data
        except Exception:
            # Fallback: usar match_jobs_ids y luego obtener las ofertas
            try:
                rpc_response = sb.rpc("match_jobs_ids", params).execute()
                matched_ids = [row["id"] for row in (rpc_response.data or [])]
                if matched_ids:
                    r = sb.table("jobs_clean").select(
                        "id, plataforma, rol_busqueda, oferta_laboral, locacion, descripcion, "
                        "sueldo, compania, habilidades, url_publicacion, fecha_publicacion, seniority"
                    ).in_("id", matched_ids[:limit]).execute()
                    ofertas = r.data or []
            except Exception as e:
                print(f"Error en búsqueda semántica: {e}")
                return []

        return ofertas[:limit]
    except Exception as e:
        print(f"Error generando embedding o buscando ofertas: {e}")
        return []


def _formatear_ofertas_contexto(ofertas: list[dict]) -> str:
    """Formatea las ofertas encontradas como contexto para el LLM."""
    if not ofertas:
        return "No se encontraron ofertas relevantes en la base de datos."

    contexto = "Ofertas laborales relevantes encontradas:\n\n"
    for i, oferta in enumerate(ofertas, 1):
        habs = oferta.get("habilidades", "")
        if isinstance(habs, str):
            habs_list = [h.strip() for h in habs.split(",") if h.strip()][:5]
            habs_str = ", ".join(habs_list)
        else:
            habs_str = str(habs)[:100]

        contexto += f"{i}. {oferta.get('oferta_laboral', 'Sin título')}\n"
        contexto += f"   Empresa: {oferta.get('compania', 'No especificada')}\n"
        contexto += f"   Ubicación: {oferta.get('locacion', 'No especificada')}\n"
        contexto += f"   Rol: {oferta.get('rol_busqueda', 'No especificado')}\n"
        if oferta.get("sueldo"):
            contexto += f"   Salario: {oferta.get('sueldo')}\n"
        contexto += f"   Habilidades: {habs_str}\n"
        contexto += f"   Descripción: {oferta.get('descripcion', '')[:200]}...\n\n"

    return contexto


def chat_rag(mensaje: str, session_id: str) -> dict:
    """
    Procesa un mensaje del usuario usando arquitectura RAG:
    1. Filtro de Intención (Groq llama-3.1-8b-instant)
    2. Historial de conversación (Redis)
    3. Búsqueda Semántica (Supabase con embeddings)
    4. Respuesta Final (Groq llama-3.3-70b-versatile)
    """
    # 1. Validar intención
    es_valida, mensaje_rechazo = _validar_intencion(mensaje)
    if not es_valida:
        return {
            "respuesta": mensaje_rechazo or "Lo siento, solo puedo responder preguntas sobre el mercado laboral IT.",
            "ofertas_encontradas": 0,
            "rechazada": True,
        }

    # 2. Recuperar historial
    historial = _get_history(session_id)

    # 3. Búsqueda semántica
    ofertas = _buscar_ofertas_semanticas(mensaje, limit=5)
    contexto_ofertas = _formatear_ofertas_contexto(ofertas)

    # 4. Generar respuesta con Groq
    if not GROQ_API_KEY:
        return {
            "respuesta": "Lo siento, el servicio de chat no está disponible en este momento.",
            "ofertas_encontradas": len(ofertas),
            "rechazada": False,
        }

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage, AssistantMessage

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=GROQ_API_KEY,
        )

        system = """Eres DevRadarBot, un asistente experto en el mercado laboral IT de Ecuador.
Tu función es ayudar a los usuarios con información sobre ofertas laborales, tecnologías demandadas, salarios y consejos de carrera.

INSTRUCCIONES:
- Responde de forma profesional, clara y centrada en los datos reales proporcionados.
- Si hay ofertas relevantes, menciona información específica de ellas (empresa, ubicación, habilidades requeridas).
- Si no hay ofertas relevantes, proporciona información general basada en tu conocimiento del mercado IT ecuatoriano.
- Mantén respuestas concisas (2-4 párrafos máximo).
- Usa el historial de conversación para mantener coherencia.
- Si el usuario pregunta algo que no está en el contexto, indica que puedes buscar más información si reformula la pregunta."""

        # Construir mensajes: historial + contexto + pregunta actual
        mensajes = [SystemMessage(content=system)]

        # Agregar historial (últimos 5 mensajes)
        for msg in historial:
            if msg.get("role") == "user":
                mensajes.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                mensajes.append(AssistantMessage(content=msg.get("content", "")))

        # Agregar contexto de ofertas y pregunta actual
        contexto_completo = f"""{contexto_ofertas}

Pregunta del usuario: {mensaje}

Responde basándote en las ofertas encontradas y el historial de la conversación."""

        mensajes.append(HumanMessage(content=contexto_completo))

        response = llm.invoke(mensajes)
        respuesta = response.content if hasattr(response, "content") else str(response)

        # Guardar mensajes en historial
        _save_message(session_id, "user", mensaje)
        _save_message(session_id, "assistant", respuesta)

        return {
            "respuesta": respuesta.strip(),
            "ofertas_encontradas": len(ofertas),
            "rechazada": False,
        }
    except Exception as e:
        print(f"Error generando respuesta con Groq: {e}")
        return {
            "respuesta": "Lo siento, ocurrió un error al procesar tu pregunta. Por favor intenta de nuevo.",
            "ofertas_encontradas": len(ofertas),
            "rechazada": False,
        }
