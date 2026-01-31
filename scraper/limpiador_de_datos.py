import json
import re
import os
import pandas as pd

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
# 🚀 EJECUCIÓN FASE 1 (SOLO LIMPIEZA)
# =============================================================================
def ejecutar_limpieza_base():
    print(f"🧹 INICIANDO FASE 1: LIMPIEZA DE DATOS (SIN IA DE SUELDOS)...")
    
    data_final = []
    ids_vistos = set()
    
    # 1. CARGAR JOOBLE
    if os.path.exists("data_cruda_jooble.json"):
        with open("data_cruda_jooble.json", "r", encoding="utf-8") as f:
            for item in json.load(f):
                data_final.append({
                    "titulo": item.get("titulo", "Sin Título"),
                    "raw_text": item.get("raw_text", ""),
                    "link": item.get("link", ""),
                    "fecha_recoleccion": item.get("fecha_recoleccion"),
                    "origen": "Jooble",
                    "salario_detectado": None,
                    "ubicacion_csv": None,
                    "empresa_detectada": item.get("empresa", item.get("company", "Confidencial"))
                })

    # 2. CARGAR CSV (MULTITRABAJOS / SCRAPY)
    if os.path.exists("ofertas_crudas.csv"):
        try:
            df = pd.read_csv("ofertas_crudas.csv", encoding='latin-1', sep=';')
            if df.shape[1] < 2: df = pd.read_csv("ofertas_crudas.csv", encoding='latin-1', sep=',')
            
            for _, row in df.iterrows():
                titulo = str(row.get("oferta_laboral", "Sin Título")).replace("PostuladoVista", "").strip()
                desc = str(row.get("descripcion", "")) + " " + str(row.get("detalle", ""))
                
                data_final.append({
                    "titulo": titulo,
                    "raw_text": desc,
                    "link": str(row.get("url_publicacion", "")),
                    "fecha_recoleccion": "2026-01-22",
                    "origen": "Multitrabajos",
                    "salario_detectado": limpiar_sueldo_csv(row.get("sueldo", "")),
                    "ubicacion_csv": str(row.get("lugar", "")),
                    "empresa_detectada": str(row.get("compania", "Confidencial"))
                })
        except: pass

    # 3. CARGAR LINKEDIN
    archivo_linkedin = "data_cruda_linkedin.json"
    if os.path.exists(archivo_linkedin):
        with open(archivo_linkedin, "r", encoding="utf-8") as f:
            for item in json.load(f):
                salario = item.get("min_amount") if item.get("min_amount") else None
                data_final.append({
                    "titulo": item.get("title", "Sin Título"),
                    "raw_text": item.get("description", ""),
                    "link": item.get("job_url", ""),
                    "fecha_recoleccion": "2026-01-23",
                    "origen": "LinkedIn",
                    "salario_detectado": salario,
                    "ubicacion_csv": item.get("location", "Ecuador"),
                    "empresa_detectada": item.get("company", "Confidencial")
                })

    # 4. PROCESAMIENTO Y FILTRADO
    resultados = []
    print(f"🔄 Analizando {len(data_final)} ofertas crudas...")
    
    for i, item in enumerate(data_final):
        link = item.get("link", "")
        if not link or link in ids_vistos: continue
        
        titulo = item.get("titulo", "Sin Título")
        raw_text = item.get("raw_text", "")
        texto_analisis = f"{titulo} {raw_text}" 
        
        # A. EXTACCIÓN DE SKILLS (REGEX)
        skills = extraer_skills_regex(texto_analisis)
        
        # B. FILTRO DE VALIDEZ
        if not es_oferta_valida(titulo, skills): continue

        # C. PREPARAR DATOS
        ubi_final = item.get("ubicacion_csv") if item.get("ubicacion_csv") else detectar_ubicacion(texto_analisis)
        salario = item.get("salario_detectado")
        if not salario: salario = "No especificado" # Default si no venía en el CSV

        registro = {
            "fuente": item.get("origen"),
            "fecha": item.get("fecha_recoleccion"),
            "titulo": titulo,
            "salario": salario, # Aquí va solo lo que encontró en el CSV/JSON original
            "ubicacion": ubi_final,
            # Guardamos las skills del Regex (VITAL para Jooble bloqueado)
            "skills": ", ".join(sorted(skills)) if skills else "Sin Detalle Técnico",
            "empresa": item.get("empresa_detectada", "Confidencial"), 
            "link": link,
            "raw_text": raw_text
        }
        resultados.append(registro)
        ids_vistos.add(link)

    # 5. GUARDAR EXCEL LIMPIO
    if resultados:
        df = pd.DataFrame(resultados)
        # Ordenamos las columnas bonito
        cols = ["fecha", "fuente", "titulo", "salario", "ubicacion", "skills", "empresa", "link", "raw_text"]
        for c in cols: 
            if c not in df.columns: df[c] = ""
        df = df[cols]
        
        archivo = "DATA_LIMPIA_SIN_SUELDOS.xlsx"
        df.to_excel(archivo, index=False)
        print(f"\n✨ ¡FASE 1 COMPLETADA!")
        print(f"📂 Archivo generado: '{archivo}'")
        print(f"📊 Total ofertas válidas (TI): {len(resultados)}")
        print("🚀 Listo para la siguiente fase (Embeddings en Nube).")
    else:
        print("❌ No quedaron registros válidos después del filtro.")

if __name__ == "__main__":
    ejecutar_limpieza_base()