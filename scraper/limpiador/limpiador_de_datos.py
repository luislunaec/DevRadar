import os
import sys
import time
import re
from datetime import datetime, timezone
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


def extraer_sueldo_numerico(valor: str | int | float | None) -> Optional[float]:
    """
    Convierte sueldo en texto o número a un único valor numérico (float).
    Acepta rangos (ej: "1500 - 2000") y devuelve el primer número o el promedio.
    Retorna None si no hay valor válido.
    """
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        try:
            return float(valor) if valor == valor else None  # evita NaN
        except (TypeError, ValueError):
            return None
    texto = str(valor).strip().lower()
    if not texto or texto in ("no especificado", "nan", "none", ""):
        return None
    # Buscar uno o más números (enteros o decimales)
    numeros = re.findall(r"[\d.,]+", texto)
    numeros_limpios = []
    for n in numeros:
        try:
            # Formato "1.500" (miles) vs "1500.50" (decimal)
            s = n.strip()
            if re.match(r"^\d+\.\d{3}$", s):  # 1.500 -> 1500
                v = float(s.replace(".", ""))
            else:
                s = s.replace(",", ".").replace(" ", "")
                v = float(s)
            if 100 <= v < 1e9:  # rango razonable en USD
                numeros_limpios.append(v)
        except ValueError:
            continue
    if not numeros_limpios:
        return None
    return sum(numeros_limpios) / len(numeros_limpios)  # promedio si hay rango


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

    # 1. CARGAR SOLO REGISTROS NO PROCESADOS (pipeline incremental)
    print("📂 Cargando ofertas crudas no procesadas de Supabase (jobs_raw donde processed = false)...")
    try:
        response = supabase.table('jobs_raw').select('*').eq('processed', False).execute()
        data_final = response.data if response.data else []
    except Exception as e:
        # Compatibilidad: si la columna processed no existe, cargar todos
        try:
            response = supabase.table('jobs_raw').select('*').execute()
            data_final = response.data if response.data else []
        except Exception as e2:
            print(f"❌ Error cargando datos: {e2}")
            return
        print(f"⚠️ Columna 'processed' no encontrada; procesando todos los registros.")

    if not data_final:
        print("✅ No hay ofertas nuevas por procesar (jobs_raw.processed = false).")
        return

    print(f"🔄 Procesando {len(data_final)} ofertas no procesadas...")

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

        # --- D. PREPARAR REGISTRO (sueldo numérico para jobs_clean) ---
        texto_sueldo = (
            analisis.sueldo_normalizado
            if analisis.sueldo_normalizado != "No especificado"
            else str(item.get("sueldo", "") or "")
        )
        sueldo_num = extraer_sueldo_numerico(texto_sueldo)

        registro = {
            "plataforma": item.get("plataforma", ""),
            "rol_busqueda": item.get("rol_busqueda", ""),
            "fecha_publicacion": item.get("fecha_publicacion", ""),
            "oferta_laboral": titulo,
            "locacion": item.get("locacion", "Ecuador"),
            "descripcion": descripcion,
            "sueldo": sueldo_num,
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

    # 3. GUARDAR EN SUPABASE (jobs_clean) Y MARCAR jobs_raw COMO PROCESADOS
    if resultados:
        print(f"\n💾 Guardando {len(resultados)} ofertas procesadas en 'jobs_clean'...")
        exitos = 0
        urls_procesados = []
        for registro in resultados:
            try:
                supabase.table('jobs_clean').upsert(registro, on_conflict='url_publicacion').execute()
                exitos += 1
                urls_procesados.append(registro["url_publicacion"])
            except Exception as e:
                print(f"⚠️ Error guardando '{registro['oferta_laboral'][:40]}...': {e}")

        print(f"✅ Éxito: {exitos}/{len(resultados)} guardados en jobs_clean.")

        # Marcar registros en jobs_raw como procesados (processed = true, processed_at = now())
        if urls_procesados:
            try:
                now_utc = datetime.now(timezone.utc).isoformat()
                supabase.table('jobs_raw').update({
                    'processed': True,
                    'processed_at': now_utc,
                }).in_('url_publicacion', urls_procesados).execute()
                print(f"✅ Marcados {len(urls_procesados)} registros en jobs_raw como processed = true.")
            except Exception as e:
                print(f"⚠️ No se pudieron marcar como procesados en jobs_raw: {e}")
    else:
        print("❌ Ninguna oferta pasó el filtro de la IA.")


if __name__ == "__main__":
    ejecutar_limpieza_ia()