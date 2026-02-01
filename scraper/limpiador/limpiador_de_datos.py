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

# --- CAMBIOS AQUÍ: Librerías de IA ---
# Importamos ChatGroq en lugar de ChatOpenAI
from langchain_groq import ChatGroq 
from langchain_openai import OpenAIEmbeddings # Mantenemos esto para vectores (o usa HuggingFace)
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
# 🤖 CLASE PROCESADORA CON IA (GROQ EDITION)
# =============================================================================
class JobAIProcessor:
    def __init__(self):
        # --- CAMBIOS AQUÍ: Configuración de Groq ---
        # Usamos Llama 3.3 70B porque es excelente siguiendo formatos JSON
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            temperature=0,
            # max_tokens=None,
            # timeout=None,
            # max_retries=2,
        )
        
        # Nota: Groq no tiene embeddings nativos aún. 
        # Seguimos usando OpenAI para vectores, o puedes cambiar a HuggingFaceEmbeddings()
        self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Configuración del parser
        self.parser = PydanticOutputParser(pydantic_object=JobAnalysis)
        
        # El Prompt para el LLM
        # Nota: Llama 3 a veces es hablador, reforzamos que solo queremos JSON
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
            # Invocamos a la IA
            return self.chain.invoke({"titulo": titulo, "descripcion": descripcion})
        except Exception as e:
            print(f"⚠️ Error analizando oferta '{titulo}' con Groq: {e}")
            # Retornamos un objeto 'vacío' seguro en caso de error
            return JobAnalysis(es_oferta_valida_tech=False, skills=[], seniority="", sueldo_normalizado="", ubicacion_tipo="")

    def generar_embedding(self, texto: str) -> List[float]:
        """Genera el vector numérico para búsqueda semántica."""
        try:
            texto_limpio = texto.replace("\n", " ")
            return self.embeddings_model.embed_query(texto_limpio)
        except Exception as e:
            print(f"⚠️ Error generando embedding: {e}")
            return []

# =============================================================================
# 🚀 EJECUCIÓN PRINCIPAL
# =============================================================================
def ejecutar_limpieza_ia():
    print(f"🤖 INICIANDO PROCESAMIENTO CON IA (GROQ)...")
    
    processor = JobAIProcessor()

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
        if not url or url in ids_vistos: continue

        titulo = item.get("oferta_laboral", "Sin Título")
        descripcion = item.get("descripcion", "")
        
        # --- A. ANÁLISIS IA (GROQ) ---
        analisis = processor.analizar_oferta(titulo, descripcion)

        # --- B. FILTRO DE VALIDEZ ---
        if not analisis.es_oferta_valida_tech:
            continue

        # --- C. GENERACIÓN DE EMBEDDING ---
        texto_a_vectorizar = f"{titulo} {' '.join(analisis.skills)}"
        vector = processor.generar_embedding(texto_a_vectorizar)

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
            "embedding": vector 
        }

        resultados.append(registro)
        ids_vistos.add(url)
        
        # Rate limiting: Groq tiene límites agresivos en cuentas free
        # Ajusta este sleep si recibes errores 429 (Too Many Requests)
        time.sleep(1) 
        if i % 5 == 0: print(f"   ⏳ Procesados {i+1}...")

    # 3. GUARDAR EN SUPABASE
    if resultados:
        print(f"\n💾 Guardando {len(resultados)} ofertas procesadas por IA en 'jobs_clean'...")
        exitos = 0
        for registro in resultados:
            try:
                supabase.table('jobs_clean').upsert(registro, on_conflict='url_publicacion').execute()
                exitos += 1
            except Exception as e:
                print(f"⚠️ Error guardando: {e}")
        
        print(f"✅ Éxito: {exitos}/{len(resultados)} guardados.")
    else:
        print("❌ Ninguna oferta pasó el filtro de la IA.")

if __name__ == "__main__":
    ejecutar_limpieza_ia()