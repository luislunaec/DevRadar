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
# --- EL PROMPT MAESTRO (ACTUALIZADO CON REGLAS DE DINERO) ---
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "Eres un experto reclutador IT. Tu tarea es extraer información estructurada en JSON. "
             "INSTRUCCIONES CRÍTICAS PARA EL SUELDO:\n"
             "1. Si encuentras un salario ANUAL (ej: $60k/year), DIVÍDELO para 12.\n"
             "2. Si es por HORA (ej: $20/hr), MULTIPLÍCALO por 160.\n"
             "3. Si hay un rango ($1000 - $2000), calcula el PROMEDIO (1500).\n"
             "4. Tu objetivo es devolver siempre el estimado MENSUAL en USD.\n"
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

    # --- BUCLE INFINITO PARA PROCESAR TODO POR LOTES ---
    ciclo = 1
    total_procesados_global = 0
    
    while True:
        print(f"\n🔄 --- INICIANDO LOTE #{ciclo} ---")
        print("📂 Cargando siguientes 1000 ofertas no procesadas de Supabase...")
        
        try:
            # Pedimos lotes de 1000 (el máximo seguro de Supabase)
            response = supabase.table('jobs_raw').select('*').eq('processed', False).limit(1000).execute()
            data_final = response.data if response.data else []
        except Exception as e:
            # Compatibilidad
            try:
                response = supabase.table('jobs_raw').select('*').limit(1000).execute()
                data_final = response.data if response.data else []
            except Exception as e2:
                print(f"❌ Error cargando datos: {e2}")
                break # Rompemos el bucle si hay error de conexión

        # CONDICIÓN DE SALIDA: Si no hay datos, terminamos
        if not data_final:
            print("🎉 ¡YA NO HAY MÁS OFERTAS PENDIENTES! (jobs_raw limpio).")
            break

        print(f"⚡ Procesando lote de {len(data_final)} ofertas...")

        resultados = []
        ids_vistos = set()
        
        # --- PROCESAMIENTO DEL LOTE ---
        for i, item in enumerate(data_final):
            url = item.get("url_publicacion", "")
            if not url or url in ids_vistos:
                continue

            titulo = item.get("oferta_laboral", "Sin Título")
            descripcion = item.get("descripcion", "")

            # A. ANÁLISIS IA
            analisis = processor.analizar_oferta(titulo, descripcion)

            # B. FILTRO
            if not analisis.es_oferta_valida_tech:
                print(f"   🚫 Filtrada: {titulo[:40]}...")
                # IMPORTANTE: Igual debemos marcarla como procesada en jobs_raw para no leerla de nuevo
                # La agregamos a una lista de "descartados" para actualizar su estado al final del lote?
                # Para simplificar, actualizaremos 'processed=True' incluso si no entra a jobs_clean
                # (Lo haremos abajo en el bloque de actualización masiva)
            else:
                # C. EMBEDDING
                texto_a_vectorizar = f"{titulo} {descripcion[:500]} {' '.join(analisis.skills)}"
                vector = processor.generar_embedding(texto_a_vectorizar)

                if vector:
                    # D. PREPARAR REGISTRO
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
            
            ids_vistos.add(url) # Agregamos al set para evitar duplicados en este lote
            
            # Feedback visual
            if (i + 1) % 10 == 0:
                print(f"   ⏳ Lote {ciclo}: {i + 1}/{len(data_final)} analizados...")

        # --- GUARDADO DEL LOTE ---
        if resultados:
            print(f"💾 Guardando {len(resultados)} ofertas VALIDAS en 'jobs_clean'...")
            for registro in resultados:
                try:
                    supabase.table('jobs_clean').upsert(registro, on_conflict='url_publicacion').execute()
                except Exception as e:
                    pass # Ignorar errores puntuales de guardado

        # --- MARCADO FINAL (CRÍTICO PARA QUE EL BUCLE AVANCE) ---
        # Marcamos TODAS las ofertas de este lote (validas y no validas) como procesadas
        # para que en la siguiente vuelta del While NO las vuelva a traer.
        urls_lote = [item.get("url_publicacion") for item in data_final if item.get("url_publicacion")]
        
        if urls_lote:
            # Actualizamos en bloques de 100 para no romper la URL request
            chunk_size = 100
            for k in range(0, len(urls_lote), chunk_size):
                chunk_urls = urls_lote[k:k + chunk_size]
                try:
                    now_utc = datetime.now(timezone.utc).isoformat()
                    supabase.table('jobs_raw').update({
                        'processed': True,
                        'processed_at': now_utc
                    }).in_('url_publicacion', chunk_urls).execute()
                except Exception as e:
                    print(f"⚠️ Error actualizando estado processed: {e}")

            print(f"✅ Lote #{ciclo} terminado. {len(urls_lote)} registros marcados como procesados.")
            total_procesados_global += len(urls_lote)
        
        ciclo += 1
        # Fin del While, vuelve arriba a cargar los siguientes 1000
    
    print("\n" + "="*60)
    print(f"🏁 PROCESO TOTAL FINALIZADO. {total_procesados_global} ofertas procesadas hoy.")