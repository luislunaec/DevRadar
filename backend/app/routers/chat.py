"""
Router para el chatbot RAG de DevRadar.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.chat_service import chat_rag

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")
    session_id: str = Field(..., min_length=1, max_length=100, description="ID de sesión para mantener historial")


class ChatResponse(BaseModel):
    respuesta: str
    ofertas_encontradas: int
    rechazada: bool


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint de chat RAG para DevRadar.
    
    Flujo:
    1. Filtro de Intención (Groq llama-3.1-8b-instant) valida si la pregunta es válida
    2. Historial (Redis) recupera últimos 5 mensajes de la sesión
    3. Búsqueda Semántica (Supabase) encuentra ofertas relevantes usando embeddings
    4. Respuesta Final (Groq llama-3.3-70b-versatile) genera respuesta con contexto
    
    Parámetros:
    - mensaje: Pregunta del usuario (máx 1000 caracteres)
    - session_id: ID único de sesión para mantener historial de conversación
    
    Retorna:
    - respuesta: Respuesta del chatbot
    - ofertas_encontradas: Número de ofertas encontradas y usadas como contexto
    - rechazada: True si la pregunta fue rechazada por el filtro de intención
    """
    try:
        resultado = chat_rag(request.mensaje, request.session_id)
        return ChatResponse(**resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando chat: {str(e)}")
