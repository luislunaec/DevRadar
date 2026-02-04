"""
Router para el chatbot RAG de DevRadar.
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.chat_service import chat_rag

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")
    session_id: str = Field(..., min_length=1, max_length=100, description="ID de sesión para mantener historial")


# Estructura para mandar los links bonitos al frontend
class FuenteDatos(BaseModel):
    titulo: str
    empresa: str
    url: str


class ChatResponse(BaseModel):
    respuesta: str
    ofertas_encontradas: int
    rechazada: bool
    # Aquí viajan los links para que tu Frontend ponga el botón "Ver Fuentes"
    fuentes: List[FuenteDatos] = []


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint de chat RAG mejorado.
    Retorna respuesta en Markdown y lista de fuentes estructurada.
    """
    try:
        resultado = chat_rag(request.mensaje, request.session_id)
        return ChatResponse(**resultado)
    except Exception as e:
        print(f"Error en endpoint chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando chat: {str(e)}")