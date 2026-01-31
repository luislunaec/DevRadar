import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import time
from supabase_helper import supabase

# --- 1. CONFIGURACIÓN ---
print("🚀 Iniciando generación de embeddings y guardado en Supabase...")

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("❌ ERROR: Falta GOOGLE_API_KEY en el .env")
    exit()

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Conectado a Google AI y Supabase")
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

# Cargar datos limpios de Supabase
print("📂 Cargando ofertas limpias de Supabase (jobs_clean)...")
try:
    response = supabase.table('jobs_clean').select('*').execute()
    data_limpia = response.data if response.data else []
    print(f"   ✓ {len(data_limpia)} ofertas limpias cargadas")
except Exception as e:
    print(f"   ❌ Error cargando datos: {e}")
    exit()

if not data_limpia:
    print("❌ No hay datos limpios para procesar. Ejecuta primero el limpiador.")
    exit()

exitos = 0

for index, item in enumerate(data_limpia):
    try:
        # 1. Recuperamos datos del formato estándar
        plataforma = str(item.get('plataforma', ''))
        rol_busqueda = str(item.get('rol_busqueda', ''))
        fecha_publicacion = str(item.get('fecha_publicacion', ''))
        oferta_laboral = str(item.get('oferta_laboral', 'Sin Título'))
        locacion = str(item.get('locacion', 'Ecuador'))
        descripcion = str(item.get('descripcion', ''))
        sueldo = str(item.get('sueldo', 'No especificado'))
        compania = str(item.get('compania', 'Confidencial'))
        habilidades = str(item.get('habilidades', ''))
        url_publicacion = str(item.get('url_publicacion', ''))
        job_clean_id = item.get('id')  # ID de la tabla jobs_clean para la relación
        
        if not url_publicacion or url_publicacion == "nan": continue
        if not job_clean_id: continue  # Necesitamos el ID para la relación

        print(f"🔄 {index+1}/{len(data_limpia)}: {oferta_laboral[:25]}...", end="\r")

        # 2. Preparar texto para embedding
        texto_para_ia = f"{oferta_laboral}. {descripcion}"
        if habilidades:
            texto_para_ia += f" Habilidades: {habilidades}"

        # 3. Generar Vector
        vector = obtener_embedding(texto_para_ia)
        if not vector:
            print(f"\n⚠️ No se pudo generar embedding para {url_publicacion[:30]}")
            continue
        
        # 4. Procesar habilidades (convertir string a lista si es necesario)
        if habilidades:
            if isinstance(habilidades, str):
                # Si viene como "JAVA, SQL, PYTHON"
                habilidades_lista = [s.strip() for s in habilidades.split(',') if s.strip()]
            else:
                habilidades_lista = habilidades if isinstance(habilidades, list) else []
        else:
            habilidades_lista = []

        # 5. Datos en formato requerido para Supabase (tabla jobs)
        datos = {
            "plataforma": plataforma,
            "rol_busqueda": rol_busqueda,
            "fecha_publicacion": fecha_publicacion,
            "oferta_laboral": oferta_laboral,
            "locacion": locacion,
            "descripcion": descripcion,
            "sueldo": sueldo,
            "compania": compania,
            "habilidades": json.dumps(habilidades_lista) if habilidades_lista else json.dumps([]),
            "url_publicacion": url_publicacion,
            "embedding": vector,
            "job_clean_id": job_clean_id  # Relación con jobs_clean
        }
        
        # 6. Enviar a Supabase (Con reintento simple)
        try:
            supabase.table('jobs').upsert(datos, on_conflict='url_publicacion').execute()
            exitos += 1
        except Exception as e_db:
            # Si falla la conexión, esperamos y seguimos
            print(f"\n⚠️ Error de red al subir oferta {index}: {e_db}")
            time.sleep(5) 
        
        # Pausa para Google
        time.sleep(1.5)

    except KeyboardInterrupt:
        print("\n🛑 Detenido por el usuario.")
        break
    except Exception as e:
        print(f"\n❌ Error inesperado item {index}: {e}")
        continue

print(f"\n\n✨ ¡MISIÓN CUMPLIDA! Se salvaron {exitos}/{len(data_limpia)} ofertas con embeddings en la nube.")