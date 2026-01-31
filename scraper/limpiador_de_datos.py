import re
import os
import pandas as pd
from supabase_helper import supabase

# =============================================================================
# 🧠 MAPA TECNOLÓGICO (REGEX SALVAVIDAS)
# =============================================================================
MAPA_TECNOLOGIAS = {
    # --- Lenguajes ---
    r'\bpython\b': 'PYTHON', r'\bjava\b': 'JAVA', r'\bjavascript\b': 'JAVASCRIPT',
    r'\btypescript\b': 'TYPESCRIPT', r'\bphp\b': 'PHP', r'c\s*#': 'C#',          
    r'\.net\b': '.NET', r'\.net core\b': '.NET CORE', r'\bscala\b': 'SCALA',
    r'\bgolang\b': 'GO', r'\bkotlin\b': 'KOTLIN', r'\bruby\b': 'RUBY',
    r'\bswift\b': 'SWIFT', r'\bflutter\b': 'FLUTTER',

    # --- Backend & Frameworks ---
    r'\bspring\b': 'SPRING', r'\bspring boot\b': 'SPRING BOOT', r'\bnodejs\b': 'NODE.JS',
    r'\bnode\b': 'NODE.JS', r'\bexpress\b': 'EXPRESS', r'\bdjango\b': 'DJANGO',
    r'\bflask\b': 'FLASK', r'\bhibernate\b': 'HIBERNATE', r'\bjpa\b': 'JPA',              
    r'\bquarkus\b': 'QUARKUS', r'\bapis?\s?rest': 'API REST',

    # --- Frontend ---
    r'\breact\b': 'REACT', r'\breact native\b': 'REACT NATIVE', r'\bangular\b': 'ANGULAR',
    r'\bvue\b': 'VUE.JS', r'\bhtml\b': 'HTML', r'\bcss\b': 'CSS', r'\bjquery\b': 'JQUERY',        
    r'\btailwind\b': 'TAILWIND', r'\bbootstrap\b': 'BOOTSTRAP',

    # --- BASES DE DATOS ---
    r'\bsql\b': 'SQL', r'\bnosql\b': 'NOSQL', r'\bmysql\b': 'MYSQL', r'\bpostgres\b': 'POSTGRESQL',
    r'\bsql server\b': 'SQL SERVER', r'\bmongodb\b': 'MONGODB', r'\boracle\b': 'ORACLE',
    r'\bhadoop\b': 'HADOOP', r'\bspark\b': 'SPARK', r'\bkafka\b': 'KAFKA', r'\betl\b': 'ETL',
    r'\binformatica\b': 'INFORMATICA (ETL)', r'\btalend\b': 'TALEND', r'\bdata lake': 'DATA LAKE',
    r'\bbig data\b': 'BIG DATA',

    # --- INFRAESTRUCTURA ---
    r'\baws\b': 'AWS', r'\bazure\b': 'AZURE', r'\bdocker\b': 'DOCKER', r'\bkubernetes\b': 'KUBERNETES',
    r'\bjenkins\b': 'JENKINS', r'\bgit\b': 'GIT', r'\bgithub\b': 'GITHUB', r'\bci/cd\b': 'CI/CD',
    r'\blinux\b': 'LINUX',

    # --- Herramientas ---
    r'\bexcel\b': 'EXCEL', r'\bpower bi\b': 'POWER BI', r'\btableau\b': 'TABLEAU',
    r'\bqa\b': 'QA/TESTING', r'\bautomatizaci[oó]n\b': 'QA AUTOMATION', 
    r'\bscrum\b': 'SCRUM', r'\bagile\b': 'AGILE', r'\bjira\b': 'JIRA',
    r'\bfigma\b': 'FIGMA', r'\bvs\s?code\b': 'VS CODE'
}

# =============================================================================
# 🕵️‍♂️ FUNCIONES AUXILIARES (LÓGICA PURA)
# =============================================================================
def detectar_ubicacion(texto_completo, default="Quito"):
    if not isinstance(texto_completo, str): return default
    texto = texto_completo.lower()
    if "remoto" in texto: return "Remoto"
    if "hibrido" in texto or "híbrido" in texto: return "Híbrido"
    if "guayaquil" in texto: return "Guayaquil"
    if "cuenca" in texto: return "Cuenca"
    return default

def extraer_skills_regex(texto):
    if not isinstance(texto, str): return []
    texto_limpio = texto.lower()
    # Limpieza básica para que el regex agarre mejor
    texto_limpio = re.sub(r'[^a-z0-9\+\.#]', ' ', texto_limpio)
    texto_limpio = f" {texto_limpio} " 
    skills = set()
    for patron, tech in MAPA_TECNOLOGIAS.items():
        if re.search(patron, texto_limpio): skills.add(tech)
    return list(skills)

def limpiar_sueldo_csv(valor):
    if pd.isna(valor) or str(valor).strip() == "" or "No especificado" in str(valor): return None
    # Limpieza de basura del CSV (ej: "US$ 1000 (Mensual)")
    t = str(valor).replace("US$", "").replace("(Mensual)", "").replace(".", "").split(",")[0].split("+")[0]
    return t.strip()

def es_oferta_valida(titulo, skills_detectadas):
    titulo = titulo.lower()
    
    # 1. FILTRO DE BASURA (Bloqueamos trabajos no-tech)
    basura = [
        "chofer", "vendedor", "cajero", "limpieza", "tesorero", "contable", 
        "recepcionista", "enfermero", "medico", "cocinero", "mesero", 
        "asesor comercial", "asesor de ventas", "call center", "atención al cliente",
        "bilingüe", "profesor de inglés", "secretaria", "asistente administrativo",
        "guardia", "bodeguero", "impulsador"
    ]
    if any(p in titulo for p in basura): return False

    # 2. LÓGICA ANTI-OFFICE (Si solo sabe Excel, chao)
    tech_real = [s for s in skills_detectadas if s not in ["EXCEL", "WORD", "ENGLISH", "OFFICE", "POWERPOINT"]]
    
    # Si tiene skills técnicas reales, PASA.
    if len(tech_real) > 0: return True

    # 3. RESCATE POR TÍTULO (Si no hay skills pero el título es claro)
    tech_keywords = [
        "desarrollador", "developer", "programador", "sistemas", "software", 
        "devops", "qa ", "tester", "datos", "data", "ti ", "it ", "informática",
        "computación", "full stack", "backend", "frontend", "tecnología"
    ]
    if any(k in titulo for k in tech_keywords): return True
    
    return False

# =============================================================================
# 🚀 EJECUCIÓN LIMPIEZA Y PROCESAMIENTO DE SCRAPERS
# =============================================================================
def ejecutar_limpieza_base():
    print(f"🧹 INICIANDO LIMPIEZA DE DATOS DE SCRAPERS...")
    
    # 1. CARGAR DATOS CRUDOS DE SUPABASE
    print("📂 Cargando ofertas crudas de Supabase (jobs_raw)...")
    try:
        response = supabase.table('jobs_raw').select('*').execute()
        data_final = response.data if response.data else []
        print(f"   ✓ {len(data_final)} ofertas crudas cargadas")
    except Exception as e:
        print(f"   ❌ Error cargando datos: {e}")
        return

    # 4. PROCESAMIENTO Y EXTRACCIÓN DE HABILIDADES
    resultados = []
    ids_vistos = set()
    print(f"\n🔄 Analizando {len(data_final)} ofertas y extrayendo habilidades...")
    
    for i, item in enumerate(data_final):
        url = item.get("url_publicacion", "")
        if not url or url in ids_vistos: continue
        
        titulo = item.get("oferta_laboral", "Sin Título")
        descripcion = item.get("descripcion", "")
        texto_analisis = f"{titulo} {descripcion}" 
        
        # A. EXTRACCIÓN DE SKILLS (REGEX)
        skills = extraer_skills_regex(texto_analisis)
        
        # B. FILTRO DE VALIDEZ
        if not es_oferta_valida(titulo, skills): continue

        # C. PREPARAR DATOS EN FORMATO FINAL
        sueldo = item.get("sueldo")
        # En jobs_clean, sueldo es TEXT, así que convertimos todo a string
        if sueldo is None or pd.isna(sueldo) or (isinstance(sueldo, str) and "No especificado" in str(sueldo)):
            sueldo = "No especificado"
        elif isinstance(sueldo, (int, float)):
            sueldo = str(sueldo)
        else:
            sueldo = str(sueldo) if sueldo else "No especificado"

        registro = {
            "plataforma": str(item.get("plataforma", "")) if item.get("plataforma") else "",
            "rol_busqueda": str(item.get("rol_busqueda", "")) if item.get("rol_busqueda") else "",
            "fecha_publicacion": str(item.get("fecha_publicacion", "")) if item.get("fecha_publicacion") else "",
            "oferta_laboral": str(titulo) if titulo else "Sin Título",
            "locacion": str(item.get("locacion", "Ecuador")) if item.get("locacion") else "Ecuador",
            "descripcion": str(descripcion) if descripcion else "",
            "sueldo": str(sueldo),
            "compania": str(item.get("compania", "Confidencial")) if item.get("compania") else "Confidencial",
            "habilidades": ", ".join(sorted(skills)) if skills else "",
            "url_publicacion": str(url) if url else ""
        }
        
        # Validar campos requeridos
        if not registro["plataforma"] or not registro["oferta_laboral"] or not registro["url_publicacion"]:
            continue
        resultados.append(registro)
        ids_vistos.add(url)

    # 5. GUARDAR EN SUPABASE (jobs_clean)
    if resultados:
        print(f"\n💾 Guardando {len(resultados)} ofertas limpias en Supabase (jobs_clean)...")
        exitos = 0
        
        for registro in resultados:
            try:
                # Asegurar que todos los campos requeridos estén presentes
                registro_limpio = {
                    'plataforma': registro.get('plataforma', ''),
                    'rol_busqueda': registro.get('rol_busqueda', ''),
                    'fecha_publicacion': registro.get('fecha_publicacion', ''),
                    'oferta_laboral': registro.get('oferta_laboral', 'Sin Título'),
                    'locacion': registro.get('locacion', 'Ecuador'),
                    'descripcion': registro.get('descripcion', ''),
                    'sueldo': registro.get('sueldo', 'No especificado'),
                    'compania': registro.get('compania', 'Confidencial'),
                    'habilidades': registro.get('habilidades', ''),
                    'url_publicacion': registro.get('url_publicacion', '')
                }
                
                # Validar campos requeridos
                if not registro_limpio['plataforma'] or not registro_limpio['oferta_laboral'] or not registro_limpio['url_publicacion']:
                    continue
                
                supabase.table('jobs_clean').upsert(registro_limpio, on_conflict='url_publicacion').execute()
                exitos += 1
            except Exception as e:
                error_msg = str(e)
                if 'duplicate key' not in error_msg.lower() and 'unique constraint' not in error_msg.lower():
                    print(f"⚠️ Error guardando oferta {registro.get('url_publicacion', '')[:30]}: {error_msg[:100]}")
        
        print(f"\n✨ ¡LIMPIEZA COMPLETADA!")
        print(f"📊 Total ofertas válidas (TI): {len(resultados)}")
        print(f"✅ {exitos}/{len(resultados)} ofertas guardadas en Supabase (jobs_clean)")
        print("🚀 Listo para generar embeddings.")
    else:
        print("❌ No quedaron registros válidos después del filtro.")

if __name__ == "__main__":
    ejecutar_limpieza_base()