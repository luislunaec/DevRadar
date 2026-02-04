"""
Servicio de Chat RAG para DevRadar - Versión "Visual & Markdown"
"""
import os
import json
from typing import Optional, List
from dotenv import load_dotenv
from app.database import get_supabase
from app.embeddings import embed_text
from app.llm import GROQ_API_KEY

# Importaciones de LangChain
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

# Redis (opcional, fallback a memoria)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

_memory_cache: dict[str, list[dict]] = {}
MAX_HISTORY = 5
SIMILARITY_THRESHOLD = 0.27


def _get_redis_client():
    if not REDIS_ENABLED:
        return None
    try:
        import redis
        return redis.from_url(REDIS_URL, decode_responses=True)
    except Exception as e:
        print(f"Redis no disponible, usando memoria: {e}")
        return None


def _get_history(session_id: str) -> list[dict]:
    redis_client = _get_redis_client()
    if redis_client:
        try:
            history_json = redis_client.lrange(f"chat:history:{session_id}", 0, MAX_HISTORY - 1)
            return [json.loads(msg) for msg in reversed(history_json)] if history_json else []
        except Exception:
            return _memory_cache.get(session_id, [])[-MAX_HISTORY:]
    return _memory_cache.get(session_id, [])[-MAX_HISTORY:]


def _save_message(session_id: str, role: str, content: str):
    msg = {"role": role, "content": content}
    redis_client = _get_redis_client()
    if redis_client:
        try:
            redis_client.lpush(f"chat:history:{session_id}", json.dumps(msg))
            redis_client.ltrim(f"chat:history:{session_id}", 0, MAX_HISTORY - 1)
            redis_client.expire(f"chat:history:{session_id}", 3600 * 24)
        except Exception:
            if session_id not in _memory_cache: _memory_cache[session_id] = []
            _memory_cache[session_id].append(msg)
    else:
        if session_id not in _memory_cache: _memory_cache[session_id] = []
        _memory_cache[session_id].append(msg)


def _validar_intencion(mensaje: str) -> tuple[bool, Optional[str]]:
    """Filtro de intención."""
    if not GROQ_API_KEY: return True, None
    try:
        llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, api_key=GROQ_API_KEY)
        
        system = """Eres el guardián de DevRadar.
        Misión: Aceptar SOLO preguntas sobre tecnología, programación, salarios IT y carrera profesional.
        Rechaza preguntas de cocina, deportes, medicina, leyes, etc.
        Responde JSON: {"es_valida": true/false, "mensaje_rechazo": "msg o null"}
        """
        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=mensaje)])
        text = response.content
        if "```" in text: text = text.split("```")[1].replace("json", "")
        data = json.loads(text)
        return data.get("es_valida", True), data.get("mensaje_rechazo")
    except Exception:
        return True, None


def _buscar_ofertas_semanticas(query: str, limit: int = 6) -> list[dict]:
    """Busca ofertas y retorna los datos crudos de Supabase."""
    try:
        query_embedding = embed_text(query)
        if not query_embedding: return []
        
        sb = get_supabase()
        params = {"query_embedding": query_embedding, "match_threshold": SIMILARITY_THRESHOLD, "match_count": limit}
        
        try:
            rpc = sb.rpc("match_jobs", params).execute()
            return rpc.data or []
        except Exception:
            # Fallback a IDs
            rpc = sb.rpc("match_jobs_ids", params).execute()
            ids = [row["id"] for row in (rpc.data or [])]
            if ids:
                r = sb.table("jobs_clean").select("*").in_("id", ids).execute()
                return r.data or []
            return []
    except Exception as e:
        print(f"Error búsqueda semántica: {e}")
        return []


def _formatear_ofertas_contexto(ofertas: list[dict]) -> str:
    """Convierte las ofertas en texto para el Prompt del LLM."""
    if not ofertas: return "No se encontraron ofertas específicas."
    
    txt = "OFERTAS ENCONTRADAS (Úsalas para responder):\n"
    for oferta in ofertas:
        txt += f"- Puesto: {oferta.get('oferta_laboral')}\n"
        txt += f"  Empresa: {oferta.get('compania')}\n"
        txt += f"  Salario: {oferta.get('sueldo')}\n"
        txt += f"  Skills: {oferta.get('habilidades')}\n"
        txt += f"  Ubicación: {oferta.get('locacion')}\n\n"
    return txt


def chat_rag(mensaje: str, session_id: str) -> dict:
    # 1. Validar
    es_valida, rechazo = _validar_intencion(mensaje)
    if not es_valida:
        return {"respuesta": rechazo, "ofertas_encontradas": 0, "rechazada": True, "fuentes": []}

    # 2. Buscar
    ofertas = _buscar_ofertas_semanticas(mensaje, limit=6)
    contexto = _formatear_ofertas_contexto(ofertas)
    
    # 3. Preparar lista de fuentes para el botón (Data para el Frontend)
    fuentes_output = []
    for of in ofertas:
        if of.get("url_publicacion"):
            fuentes_output.append({
                "titulo": of.get("oferta_laboral", "Oferta IT"),
                "empresa": of.get("compania", "Empresa Confidencial"),
                "url": of.get("url_publicacion")
            })

    # 4. Generar Respuesta (El "Makeover" con Markdown)
    if not GROQ_API_KEY:
        return {"respuesta": "Sin servicio de IA.", "ofertas_encontradas": 0, "rechazada": False, "fuentes": []}

    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.6, api_key=GROQ_API_KEY)

        system_prompt = """Eres DevRadar, el asistente más cool y experto en empleo IT de Ecuador.
        
        TU OBJETIVO: Dar respuestas visualmente atractivas, directas y útiles.
        
        REGLAS DE FORMATO (OBLIGATORIO USAR MARKDOWN):
        1. Usa **Negritas** para resaltar salarios, tecnologías y empresas clave.
        2. Usa ### Títulos Pequeños para separar ideas (ej: "### 💰 Rango Salarial", "### 🛠️ Tecnologías Top").
        3. Usa Listas (guiones -) para enumerar requisitos o puntos clave.
        4. Usa Emojis de forma inteligente para hacer el texto amigable (🚀, 💻, 💸, 🇪🇨).
        
        ESTRUCTURA DE RESPUESTA:
        - Empieza con una frase gancho o resumen directo.
        - Desarrolla el análisis de las ofertas encontradas.
        - NO pongas los enlaces/URLs en el texto (se mostrarán en un botón aparte).
        - Si no hay salario exacto, da estimaciones basadas en tu conocimiento general pero aclara que es estimado.
        
        CONTEXTO:
        Usa EXCLUSIVAMENTE la información de las ofertas provistas abajo para los detalles específicos.
        """

        mensajes = [SystemMessage(content=system_prompt)]
        
        # Historial
        historial = _get_history(session_id)
        for m in historial:
            cls = HumanMessage if m["role"] == "user" else AIMessage
            mensajes.append(cls(content=m["content"]))

        # Input actual
        final_prompt = f"""
        {contexto}
        
        PREGUNTA DEL USUARIO: {mensaje}
        """
        mensajes.append(HumanMessage(content=final_prompt))

        response = llm.invoke(mensajes)
        respuesta_texto = response.content

        # Guardar
        _save_message(session_id, "user", mensaje)
        _save_message(session_id, "assistant", respuesta_texto)

        return {
            "respuesta": respuesta_texto,
            "ofertas_encontradas": len(ofertas),
            "rechazada": False,
            "fuentes": fuentes_output # <--- Aquí van los links para tu botón
        }

    except Exception as e:
        print(f"Error LLM: {e}")
        return {"respuesta": "Error técnico.", "ofertas_encontradas": 0, "rechazada": False, "fuentes": []}