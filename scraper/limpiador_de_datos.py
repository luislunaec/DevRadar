import os
import time
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from supabase_helper import supabase

# Librerías de IA
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# Cargar variables de entorno
load_dotenv()

# =============================================================================
# 🧠 MODELO DE DATOS (ESTRUCTURA QUE QUEREMOS DE LA IA)
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
# 🤖 CLASE PROCESADORA CON IA
# =============================================================================
class JobAIProcessor:
    def __init__(self):
        # Usamos gpt-4o-mini porque es muy económico y excelente para extracción
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Configuración del parser para obligar a la IA a devolver JSON válido
        self.parser = PydanticOutputParser(pydantic_object=JobAnalysis)
        
        # El Prompt para el LLM
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un experto reclutador IT. Tu trabajo es extraer información técnica precisa de ofertas de trabajo. "
                       "Ignora ofertas que no sean del rubro tecnológico. \n{format_instructions}"),
            ("human", "Analiza la siguiente oferta:\nTITULO: {titulo}\nDESCRIPCIÓN: {descripcion}")
        ]).partial(format_instructions=self.parser.get_format_instructions())

        self.chain = self.prompt | self.llm | self.parser

    def analizar_oferta(self, titulo: str, descripcion: str) -> JobAnalysis:
        """Envía el texto a la IA y retorna un objeto estructurado."""
        try:
            # Invocamos a la IA
            return self.chain.invoke({"titulo": titulo, "descripcion": descripcion})
        except Exception as e:
            print(f"⚠️ Error analizando oferta '{titulo}': {e}")
            # Retornamos un objeto 'vacío' seguro en caso de error de API
            return JobAnalysis(es_oferta_valida_tech=False, skills=[], seniority="", sueldo_normalizado="", ubicacion_tipo="")

    def generar_embedding(self, texto: str) -> List[float]:
        """Genera el vector numérico para búsqueda semántica."""
        try:
            # Limpiamos saltos de línea para mejor calidad del embedding
            texto_limpio = texto.replace("\n", " ")
            return self.embeddings_model.embed_query(texto_limpio)
        except Exception as e:
            print(f"⚠️ Error generando embedding: {e}")
            return []

# =============================================================================
# 🚀 EJECUCIÓN PRINCIPAL
# =============================================================================
def ejecutar_limpieza_ia():
    print(f"🤖 INICIANDO PROCESAMIENTO CON IA...")
    
    processor = JobAIProcessor()

    # 1. CARGAR DATOS CRUDOS
    print("📂 Cargando ofertas crudas de Supabase (jobs_raw)...")
    try:
        # Traemos solo los que no están procesados (puedes ajustar esta lógica)
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
        texto_completo = f"{titulo}. {descripcion}"

        # --- A. ANÁLISIS IA (EXTRACCIÓN) ---
        analisis = processor.analizar_oferta(titulo, descripcion)

        # --- B. FILTRO DE VALIDEZ ---
        if not analisis.es_oferta_valida_tech:
            # Opcional: Podrías loguear qué ofertas se descartan
            continue

        # --- C. GENERACIÓN DE EMBEDDING (VECTOR) ---
        # Vectorizamos skills + titulo para búsqueda eficiente
        texto_a_vectorizar = f"{titulo} {' '.join(analisis.skills)}"
        vector = processor.generar_embedding(texto_a_vectorizar)

        # --- D. PREPARAR REGISTRO ---
        registro = {
            "plataforma": item.get("plataforma", ""),
            "rol_busqueda": item.get("rol_busqueda", ""),
            "fecha_publicacion": item.get("fecha_publicacion", ""),
            "oferta_laboral": titulo,
            "locacion": item.get("locacion", "Ecuador"), # O usar analisis.ubicacion_tipo
            "descripcion": descripcion,
            "sueldo": analisis.sueldo_normalizado if analisis.sueldo_normalizado != "No especificado" else str(item.get("sueldo", "")),
            "compania": item.get("compania", "Confidencial"),
            "habilidades": ", ".join(analisis.skills), # Guardamos como string separado por comas
            "seniority": analisis.seniority, # Nuevo campo enriquecido
            "url_publicacion": url,
            "embedding": vector # Asegúrate que tu DB soporte vectores
        }

        resultados.append(registro)
        ids_vistos.add(url)
        
        # Rate limiting simple para no saturar
        if i % 10 == 0: print(f"   ⏳ Procesados {i+1}...")

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