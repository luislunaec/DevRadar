"""
Servicio de IA para el Backend.
Maneja Embeddings (HuggingFace) y Validaciones Inteligentes (Groq).
"""
import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

# Cargar variables de entorno (.env)
load_dotenv()

# ==========================================
# 1. MODELO DE EMBEDDINGS (HuggingFace)
# ==========================================
# Se inicializa una sola vez al arrancar
_embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}, 
)

def get_embedding(text: str) -> list[float]:
    """Genera vector de 384 dimensiones para búsquedas semánticas."""
    try:
        if not text: return []
        texto_limpio = text.replace("\n", " ").strip()
        return _embeddings_model.embed_query(texto_limpio)
    except Exception as e:
        print(f"⚠️ Error generando embedding en backend: {e}")
        return []

# ==========================================
# 2. MODELO DE VALIDACIÓN (Groq / Llama 3)
# ==========================================

class ValidationResult(BaseModel):
    is_tech: bool = Field(description="True si es tecnología, rol IT, lenguaje, framework o herramienta dev. False si es comida, trago, ciudad, etc.")
    suggested_correction: str | None = Field(description="Corrección del término si está mal escrito (ej: 'pyton'->'python'). Si es válido, null.")

def validar_termino_con_ia(query: str) -> ValidationResult:
    """Consulta a Groq para saber si el término vale la pena buscarlo."""
    try:
        # Usamos Llama 3.3 Versatile (Rápido y barato)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️ Faltan GROQ_API_KEY, saltando validación.")
            return ValidationResult(is_tech=True, suggested_correction=None)

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=api_key
        )
        
        # Estructura de salida estricta
        structured_llm = llm.with_structured_output(ValidationResult)
        
        system_msg = (
            "Eres un validador estricto para un buscador de empleos IT. "
            "Tu trabajo: Filtrar búsquedas basura. "
            "REGLAS: "
            "1. Si buscan comida, marcas de licor (ej: 'tropico', 'pilsener'), deportes o ciudades -> is_tech=False. "
            "2. Si es una tecnología real (Java, Python, AWS, Scrum) -> is_tech=True. "
            "3. Si está mal escrito, corrígelo en 'suggested_correction'."
        )
        
        return structured_llm.invoke(f"{system_msg} Analiza: '{query}'")
        
    except Exception as e:
        print(f"⚠️ Error validando con Groq: {e}")
        # Si falla la IA, dejamos pasar todo por seguridad (Fail Open)
        return ValidationResult(is_tech=True, suggested_correction=None)