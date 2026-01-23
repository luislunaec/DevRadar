import json
import re
import os
import pandas as pd

# =============================================================================
# ⚙️ CONFIGURACIÓN
# =============================================================================
PROMEDIO_MERCADO_TI = 906 

# =============================================================================
# 🧠 MAPA DE SKILLS (V9)
# =============================================================================
MAPA_TECNOLOGIAS = {
    # --- Lenguajes de programacion ---
    r'\bpython\b': 'PYTHON', r'\bjava\b': 'JAVA', r'\bjs\b': 'JAVASCRIPT', r'\bjavascript\b': 'JAVASCRIPT',
    r'\bts\b': 'TYPESCRIPT', r'\btypescript\b': 'TYPESCRIPT', r'\bphp\b': 'PHP', r'c\s*#': 'C#',          
    r'\.net\b': '.NET', r'\.net core\b': '.NET CORE', r'\bvb\b': 'VISUAL BASIC', r'\bvb\.net\b': 'VISUAL BASIC',   
    r'\bcpp\b': 'C++', r'c\s*\+\+': 'C++', r'\bscala\b': 'SCALA', r'\bgolang\b': 'GO',              
    r'\bkotlin\b': 'KOTLIN', r'\bruby\b': 'RUBY', r'\bswift\b': 'SWIFT', r'\bflutter\b': 'FLUTTER',              
    # --- Backend ---
    r'\bspring\b': 'SPRING', r'\bspring boot\b': 'SPRING BOOT', r'\bnodejs\b': 'NODE.JS', r'\bnode\b': 'NODE.JS',
    r'\bexpress\b': 'EXPRESS', r'\bdjango\b': 'DJANGO', r'\bflask\b': 'FLASK', r'\bhibernate\b': 'HIBERNATE', 
    r'\bjpa\b': 'JPA', r'\bapis?\s?rest': 'API REST',              
    # --- Frontend ---
    r'\breact\b': 'REACT', r'\breact native\b': 'REACT NATIVE', r'\bangular\b': 'ANGULAR', r'\bvue\b': 'VUE.JS',
    r'\bhtml\b': 'HTML', r'\bcss\b': 'CSS', r'\bjquery\b': 'JQUERY', r'\btailwind\b': 'TAILWIND', r'\bbootstrap\b': 'BOOTSTRAP',              
    # --- Persistencia de datos ---
    r'\bsql\b': 'SQL', r'\bnosql\b': 'NOSQL', r'\bmysql\b': 'MYSQL', r'\bpostgres\b': 'POSTGRESQL',
    r'\bsql server\b': 'SQL SERVER', r'\bmongodb\b': 'MONGODB', r'\boracle\b': 'ORACLE', r'\bhadoop\b': 'HADOOP',
    r'\bspark\b': 'SPARK', r'\bkafka\b': 'KAFKA', r'\betl\b': 'ETL', r'\bbig data\b': 'BIG DATA', r'\bpl/?sql\b': 'PL/SQL',         
    # --- Nubes de infraestructura---
    r'\baws\b': 'AWS', r'\bazure\b': 'AZURE', r'\bgcp\b': 'GOOGLE CLOUD', r'\bdocker\b': 'DOCKER',
    r'\bkubernetes\b': 'KUBERNETES', r'\bk8s\b': 'KUBERNETES', r'\bjenkins\b': 'JENKINS', r'\bgit\b': 'GIT',
    r'\bci/?\s?cd\b': 'CI/CD', r'\blinux\b': 'LINUX', r'\bterraform\b': 'TERRAFORM',    
    # --- Herramientas y metodologias Agiles ---
    r'\bexcel\b': 'EXCEL', r'\bpower bi\b': 'POWER BI', r'\bpbi\b': 'POWER BI', r'\btableau\b': 'TABLEAU',
    r'\bqa\b': 'QA/TESTING', r'\bautomatizaci[oó]n\b': 'QA AUTOMATION', r'\bselenium\b': 'SELENIUM',      
    r'\bscrum\b': 'SCRUM', r'\bagile\b': 'AGILE', r'\bjira\b': 'JIRA', r'\bfigma\b': 'FIGMA'     
}

# =============================================================================
# 🕵️‍♂️ FUNCIONES
# =============================================================================
def detectar_ubicacion(texto_completo, default="Quito"):
    if not isinstance(texto_completo, str): return default
    texto = texto_completo.lower()
    if "remoto" in texto: return "Remoto"
    if "hibrido" in texto or "híbrido" in texto: return "Híbrido"
    if "guayaquil" in texto: return "Guayaquil"
    if "cuenca" in texto: return "Cuenca"
    return default

def extraer_skills(texto):
    if not isinstance(texto, str): return []
    texto_limpio = texto.lower()
    texto_limpio = re.sub(r'[^a-z0-9\+\.#]', ' ', texto_limpio)
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    texto_limpio = f" {texto_limpio} " 
    skills = set()
    for patron, tech in MAPA_TECNOLOGIAS.items():
        if re.search(patron, texto_limpio): skills.add(tech)
    return list(skills)

def limpiar_sueldo_csv(valor):
    if pd.isna(valor) or str(valor).strip() == "" or "No especificado" in str(valor): return None
    t = str(valor).replace("US$", "").replace("(Mensual)", "").replace(".", "").split(",")[0].split("+")[0]
    return t.strip()

def es_oferta_valida(titulo, skills_detectadas):
    titulo = titulo.lower()
    basura = ["chofer", "vendedor", "cajero", "limpieza", "tesorero", "contable", "recepcionista", "enfermero", "medico", "cocinero", "mesero"]
    if any(p in titulo for p in basura): return False
    tech_real = [s for s in skills_detectadas if s not in ["EXCEL", "WORD", "ENGLISH", "OFFICE"]]
    if len(tech_real) > 0: return True
    tech_keywords = ["desarrollador", "developer", "programador", "sistemas", "software", "devops", "qa ", "tester", "datos", "data", "ti ", "it "]
    if any(k in titulo for k in tech_keywords): return True
    return False

def calcular_competitividad(salario_txt):
    if not salario_txt or salario_txt == "No especificado": return "N/A"
    try:
        monto = float(str(salario_txt).replace(".","").replace(",",""))
        if monto > 10000: monto /= 100
        diff = monto - PROMEDIO_MERCADO_TI
        if diff > 50: return "ENCIMA 🟢"
        elif diff < -50: return "DEBAJO 🔴"
        else: return "PROMEDIO 🟡"
    except: return "N/A"

# =============================================================================
# 🚀 EJECUCIÓN MAESTRA (CORREGIDA)
# =============================================================================
def ejecutar_limpieza_completa():
    print(f"🧹 EJECUTANDO LIMPIEZA V11 (ARREGLO DE EMPRESAS JOOBLE)...")
    
    data_final = []
    ids_vistos = set()
    
    # --- 1. CARGAR JOOBLE (CORREGIDO) ---
    if os.path.exists("data_cruda_jooble.json"):
        with open("data_cruda_jooble.json", "r", encoding="utf-8") as f:
            jooble = json.load(f)
            print(f"📥 Jooble: {len(jooble)} registros.")
            for item in jooble:
                # Normalizamos y tratamos de rescatar el nombre de la empresa
                data_final.append({
                    "titulo": item.get("titulo", "Sin Título"),
                    "raw_text": item.get("raw_text", ""),
                    "link": item.get("link", ""),
                    "fecha_recoleccion": item.get("fecha_recoleccion"),
                    "origen": "Jooble",
                    "salario_csv": None,
                    "ubicacion_csv": None,
                    # AQUÍ ESTÁ EL ARREGLO: Buscamos 'empresa' o 'company', si no hay, 'Confidencial'
                    "empresa_detectada": item.get("empresa", item.get("company", "Confidencial"))
                })

    # --- 2. CARGAR CSV AMIGO ---
    if os.path.exists("ofertas_crudas.csv"):
        try:
            try: df = pd.read_csv("ofertas_crudas.csv", encoding='utf-8', sep=',')
            except: df = pd.read_csv("ofertas_crudas.csv", encoding='latin-1', sep=';')
            if df.shape[1] < 2: df = pd.read_csv("ofertas_crudas.csv", encoding='latin-1', sep=',')
            
            print(f"📥 CSV Amigo: {len(df)} registros.")
            for _, row in df.iterrows():
                titulo = str(row.get("oferta_laboral", "Sin Título")).replace("PostuladoVista", "").strip()
                desc = str(row.get("descripcion", "")) + " " + str(row.get("detalle", "")) + " " + str(row.get("rol_busqueda", ""))
                
                data_final.append({
                    "titulo": titulo,
                    "raw_text": desc,
                    "link": str(row.get("url_publicacion", "")),
                    "fecha_recoleccion": "2026-01-22",
                    "origen": "Multitrabajos",
                    "salario_csv": limpiar_sueldo_csv(row.get("sueldo", "")),
                    "ubicacion_csv": str(row.get("lugar", "")),
                    # Para el CSV, el nombre ya viene listo
                    "empresa_detectada": str(row.get("compania", "Confidencial"))
                })
        except: pass

    # --- 3. PROCESAMIENTO ---
    resultados = []
    print(f"🔄 Procesando {len(data_final)} ofertas totales...")
    
    for item in data_final:
        link = item.get("link", "")
        if link in ids_vistos: continue
        
        titulo = item.get("titulo", "Sin Título")
        raw_text = item.get("raw_text", "")
        texto_analisis = f"{titulo} {raw_text}" 
        
        # A. Skills y Filtro
        skills = extraer_skills(texto_analisis)
        if not es_oferta_valida(titulo, skills): continue

        # B. Ubicación y Salario
        ubi_final = item.get("ubicacion_csv") if item.get("ubicacion_csv") else detectar_ubicacion(texto_analisis)
        salario = item.get("salario_csv") if item.get("salario_csv") else "No especificado"

        registro = {
            "fuente": item.get("origen"),
            "fecha": item.get("fecha_recoleccion"),
            "titulo": titulo,
            "salario": salario,
            "competitividad": calcular_competitividad(salario),
            "ubicacion": ubi_final,
            "skills": ", ".join(sorted(skills)) if skills else "Sin Detalle Técnico",
            # AQUÍ ESTÁ EL ARREGLO FINAL: Usamos el nombre detectado, NO el texto fijo
            "empresa": item.get("empresa_detectada", "Confidencial"), 
            "link": link
        }
        resultados.append(registro)
        ids_vistos.add(link)

    # --- GUARDAR ---
    if resultados:
        df = pd.DataFrame(resultados)
        # Aseguramos orden de columnas
        cols = ["fecha", "fuente", "titulo", "salario", "competitividad", "ubicacion", "skills", "empresa", "link"]
        for c in cols: 
            if c not in df.columns: df[c] = ""
        df = df[cols]
        
        df.to_excel("TESIS_DATA_FINAL_V11.xlsx", index=False)
        print(f"¡LISTO! {len(resultados)} ofertas limpias guardadas en 'TESIS_DATA_FINAL.xlsx'")
    else:
        print("Algo salió mal, no hay datos.")

if __name__ == "__main__":
    ejecutar_limpieza_completa()