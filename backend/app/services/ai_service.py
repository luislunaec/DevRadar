"""
Servicio de IA para el Backend.
Usa HuggingFace local para mantener consistencia con el limpiador.
"""
from langchain_huggingface import HuggingFaceEmbeddings

# Inicializamos el modelo UNA SOLA VEZ al arrancar el módulo.
# Usamos exactamente la misma configuración que tu script 'limpiador'.
_embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}, 
)

def get_embedding(text: str) -> list[float]:
    """
    Genera un vector de 384 dimensiones para el texto dado.
    """
    try:
        # Limpieza básica igual que en tu scraper
        texto_limpio = text.replace("\n", " ").strip()
        return _embeddings_model.embed_query(texto_limpio)
    except Exception as e:
        print(f"⚠️ Error generando embedding en backend: {e}")
        return []