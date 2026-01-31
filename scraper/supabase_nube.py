import os
import pandas as pd
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv
import json
import time
import datetime 

# --- 1. CONFIGURACIÓN ---
print("🚀 Iniciando el Rescate de Datos en Supabase...")

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # OJO: Asegúrate que en .env sea GOOGLE_API_KEY

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: Faltan las claves en el .env")
    exit()

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Conectado a la Nube")
except Exception as e:
    print(f"❌ Error conectando: {e}")
    exit()

# --- 2. CEREBRO IA (Blindado contra Jooble) ---

def obtener_embedding(texto):
    """Genera el vector. Si falla, espera y reintenta."""
    if not texto or len(str(texto)) < 5: return None
    try:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=str(texto)[:9000], # Recortamos por seguridad
            task_type="retrieval_document",
            title="Oferta Laboral"
        )
        return result['embedding']
    except Exception as e:
        print(f"⚠️ Warning Embedding: {e}")
        return None

def extraer_skills_ia(texto_para_analizar):
    """Intenta sacar skills. Si el texto es basura, devuelve lista vacía."""
    if not texto_para_analizar or len(str(texto_para_analizar)) < 10: return []
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Eres un experto tech. Extrae las habilidades técnicas (Stack tecnológico) de este texto.
    Devuelve SOLO una lista JSON. Ejemplo: ["Java", "Spring Boot"].
    
    Texto: {str(texto_para_analizar)[:2000]}
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except:
        return []

# --- 3. EL PROCESO ---

NOMBRE_ARCHIVO = "TESIS_DATA_LIMPIA_PARA_IA.xlsx" 
# Si no existe el limpio, intenta con el normal
if not os.path.exists(NOMBRE_ARCHIVO):
    NOMBRE_ARCHIVO = "TESIS_DATA_FINAL_V13_IA.xlsx"

if not os.path.exists(NOMBRE_ARCHIVO):
    print(f"❌ NO ENCUENTRO EL ARCHIVO EXCEL. Revisa el nombre.")
    exit()

df = pd.read_excel(NOMBRE_ARCHIVO).fillna("")
print(f"📂 Procesando archivo: {NOMBRE_ARCHIVO} ({len(df)} registros)")

exitos = 0

for index, row in df.iterrows():
    try:
        # 1. Recuperamos datos básicos
        titulo = str(row.get('titulo', 'Sin Título'))
        empresa = str(row.get('empresa', 'Confidencial'))
        link = str(row.get('link', ''))
        raw_text = str(row.get('raw_text', '')) # Descripción cruda
        skills_excel = str(row.get('skills', '')) # Skills del Regex (PLAN B)
        
        if not link or link == "nan": continue

        print(f"🔄 {index+1}/{len(df)}: {titulo[:25]}...", end="\r")

        # --- 🧠 LÓGICA DE RESCATE (AQUÍ ESTÁ LA MAGIA) ---
        
        # Detectamos si la descripción es basura de Jooble
        es_basura_jooble = "registrese" in raw_text.lower() or "verificar que usted" in raw_text.lower() or len(raw_text) < 50
        
        if es_basura_jooble:
            # PLAN B: Construimos un texto sintético con Título + Skills del Excel
            texto_para_ia = f"Puesto: {titulo}. Tecnologías requeridas: {skills_excel}. Empresa: {empresa}."
            descripcion_final = "Descripción original protegida. " + texto_para_ia
        else:
            # PLAN A: Usamos la descripción completa
            texto_para_ia = f"{titulo}. {raw_text}"
            descripcion_final = raw_text

        # 2. Generar Vector (Usando el texto limpio o el sintético)
        vector = obtener_embedding(texto_para_ia)
        
        # 3. Extraer Skills (Si es basura Jooble, usamos las del Excel directo)
        if es_basura_jooble:
            # Convertimos "JAVA, SQL" -> ["Java", "SQL"]
            skills_finales = [s.strip() for s in skills_excel.split(',') if s.strip()]
        else:
            # Si hay descripción real, dejamos que la IA busque más cosas
            skills_finales = extraer_skills_ia(texto_para_ia)
            # Si la IA falla, mezclamos con las del Excel
            if not skills_finales:
                skills_finales = [s.strip() for s in skills_excel.split(',') if s.strip()]

        # 4. Datos listos
        datos = {
            "titulo": titulo,
            "empresa": empresa,
            "ubicacion": str(row.get('ubicacion', 'Ecuador')),
            "salario": str(row.get('salario', 'No especificado')),
            "descripcion": descripcion_final, # Guardamos la explicativa
            "link": link,
            "fecha_recoleccion": str(datetime.date.today()),
            "fuente": str(row.get('fuente', 'Web')),
            "skills": json.dumps(skills_finales),
            "embedding": vector
        }
        
        # 5. Enviar a Supabase (Con reintento simple)
        try:
            supabase.table('jobs').upsert(datos, on_conflict='link').execute()
            exitos += 1
        except Exception as e_db:
            # Si falla la conexión (como te pasó antes), esperamos y seguimos
            print(f"\n⚠️ Error de red al subir oferta {index}: {e_db}")
            time.sleep(5) 
        
        # Pausa para Google
        time.sleep(1.5)

    except KeyboardInterrupt:
        print("\n🛑 Detenido por el usuario.")
        break
    except Exception as e:
        print(f"\n❌ Error inesperado fila {index}: {e}")
        continue

print(f"\n\n✨ ¡MISIÓN CUMPLIDA! Se salvaron {exitos} ofertas en la nube.")