import os
import sys
import time
from typing import List, Optional

# Permitir imports cuando se ejecuta directamente desde limpiador/
_scraper_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scraper_root not in sys.path:
    sys.path.insert(0, _scraper_root)

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from db.supabase_helper import supabase

# --- LLM: Groq ---
from langchain_groq import ChatGroq

# --- Embeddings: HuggingFace (local, gratuito, sin otra API key) ---
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# Cargar variables de entorno
load_dotenv()

# =============================================================================
# 🧠 MODELO DE DATOS
# =============================================================================
class JobAnalysis(BaseModel):
    """Estructura de salida estricta para el análisis de la oferta."""
    es_oferta_valida_tech: bool = Field(
        description="True si es un trabajo de tecnología (Desarrollo, Data, QA, DevOps, Producto). False si es chofer, ventas, medicina, etc."
    )
    skills: List[str] = Field(
        description="Lista de habilidades técnicas encontradas (ej: Python, React, AWS, SQL). Normalizadas a mayúsculas."
    )
    seniority: str = Field(
        description="Nivel de experiencia: Trainee, Junior, Semi-Senior, Senior, Lead, o 'No especificado'."
    )
    sueldo_normalizado: str = Field(
        description="El sueldo extraído limpio si existe, o 'No especificado'."
    )
    ubicacion_tipo: str = Field(
        description="Remoto, Híbrido o Presencial."
    )

# =============================================================================
# 🤖 CLASE PROCESADORA CON IA (TODO GROQ + HUGGINGFACE)
# =============================================================================
class JobAIProcessor:
    def __init__(self):
        # --- LLM: Groq con Llama 3.3 70B ---
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
        )

        # --- Embeddings: HuggingFace sentence-transformers (local, gratuito) ---
        # all-MiniLM-L6-v2 es el modelo estándar: rápido, ligero (90MB), muy buena calidad.
        # Se descarga automáticamente la primera vez (~5 seg).
        # Genera vectores de 384 dimensiones.
        self.embeddings_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},          # "cuda" si tienes GPU
            encode_kwargs={"normalize_embeddings": True},  # Normalizar mejora coseno similarity
        )

        # Configuración del parser
        self.parser = PydanticOutputParser(pydantic_object=JobAnalysis)

        # El Prompt para el LLM
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto reclutador IT. Tu tarea es extraer información estructurada en JSON. "
                       "NO incluyas texto introductorio ni explicaciones, solo el JSON raw. "
                       "Ignora ofertas que no sean del rubro tecnológico. \n{format_instructions}"),
            ("human", "Analiza la siguiente oferta:\nTITULO: {titulo}\nDESCRIPCIÓN: {descripcion}")
        ]).partial(format_instructions=self.parser.get_format_instructions())

        self.chain = self.prompt | self.llm | self.parser

    def analizar_oferta(self, titulo: str, descripcion: str) -> JobAnalysis:
        """Envía el texto a Groq y retorna un objeto estructurado."""
        try:
            return self.chain.invoke({"titulo": titulo, "descripcion": descripcion})
        except Exception as e:
            print(f"⚠️ Error analizando oferta '{titulo}' con Groq: {e}")
            return JobAnalysis(
                es_oferta_valida_tech=False,
                skills=[],
                seniority="No especificado",
                sueldo_normalizado="No especificado",
                ubicacion_tipo="No especificado",
            )

    def generar_embedding(self, texto: str) -> List[float]:
        """Genera el vector numérico usando HuggingFace (local, sin API externa)."""
        try:
            texto_limpio = texto.replace("\n", " ").strip()
            # embed_query retorna List[float] directamente
            return self.embeddings_model.embed_query(texto_limpio)
        except Exception as e:
            print(f"⚠️ Error generando embedding: {e}")
            return []

# =============================================================================
# 🚀 EJECUCIÓN PRINCIPAL
# =============================================================================
def ejecutar_limpieza_ia():
    print("🤖 INICIANDO PROCESAMIENTO CON IA (GROQ + HUGGINGFACE EMBEDDINGS)...")

    processor = JobAIProcessor()
    print("✅ Modelos cargados correctamente.")

    # 1. CARGAR DATOS CRUDOS
    print("📂 Cargando ofertas crudas de Supabase (jobs_raw)...")
    try:
        response = supabase.table('jobs_raw').select('*').execute()
        data_final = response.data if response.data else []
    except Exception as e:
        print(f"❌ Error cargando datos: {e}")
        return

    print(f"🔄 Procesando {len(data_final)} ofertas...")

    resultados = []
    ids_vistos = set()

    for i, item in enumerate(data_final):
        url = item.get("url_publicacion", "")
        if not url or url in ids_vistos:
            continue

        titulo = item.get("oferta_laboral", "Sin Título")
        descripcion = item.get("descripcion", "")

        # --- A. ANÁLISIS IA (GROQ) ---
        analisis = processor.analizar_oferta(titulo, descripcion)

        # --- B. FILTRO DE VALIDEZ ---
        if not analisis.es_oferta_valida_tech:
            print(f"   🚫 Filtrada (no es tech): {titulo[:60]}...")
            continue

        # --- C. GENERACIÓN DE EMBEDDING (HUGGINGFACE, LOCAL) ---
        texto_a_vectorizar = f"{titulo} {descripcion[:500]} {' '.join(analisis.skills)}"
        vector = processor.generar_embedding(texto_a_vectorizar)

        if not vector:
            print(f"   ⚠️ Skipped por embedding vacío: {titulo[:60]}...")
            continue

        # --- D. PREPARAR REGISTRO ---
        registro = {
            "plataforma": item.get("plataforma", ""),
            "rol_busqueda": item.get("rol_busqueda", ""),
            "fecha_publicacion": item.get("fecha_publicacion", ""),
            "oferta_laboral": titulo,
            "locacion": item.get("locacion", "Ecuador"),
            "descripcion": descripcion,
            "sueldo": analisis.sueldo_normalizado if analisis.sueldo_normalizado != "No especificado" else str(item.get("sueldo", "")),
            "compania": item.get("compania", "Confidencial"),
            "habilidades": ", ".join(analisis.skills),
            "seniority": analisis.seniority,
            "url_publicacion": url,
            "embedding": vector,
        }

        resultados.append(registro)
        ids_vistos.add(url)

        # Rate limiting para Groq (los embeddings son locales, no generan tráfico de API)
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"   ⏳ Procesados {i + 1}/{len(data_final)}...")

    # 3. GUARDAR EN SUPABASE
    if resultados:
        print(f"\n💾 Guardando {len(resultados)} ofertas procesadas en 'jobs_clean'...")
        exitos = 0
        for registro in resultados:
            try:
                supabase.table('jobs_clean').upsert(registro, on_conflict='url_publicacion').execute()
                exitos += 1
            except Exception as e:
                print(f"⚠️ Error guardando '{registro['oferta_laboral'][:40]}...': {e}")

        print(f"✅ Éxito: {exitos}/{len(resultados)} guardados en jobs_clean.")
    else:
        print("❌ Ninguna oferta pasó el filtro de la IA.")


if __name__ == "__main__":
    ejecutar_limpieza_ia()