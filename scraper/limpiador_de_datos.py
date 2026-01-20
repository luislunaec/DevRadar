import json
import pandas as pd
import re
import os
from datetime import datetime

# --- 🧠 EL CEREBRO: DICCIONARIO DE TECNOLOGÍAS ---
# Este es el mapa que usamos para buscar en el texto crudo.
MAPA_TECNOLOGIAS = {
    # Lenguajes
    r'\bpython\b': 'PYTHON',
    r'\bjava\b': 'JAVA',
    r'\bjavascript\b': 'JAVASCRIPT',
    r'\btypescript\b': 'TYPESCRIPT',
    r'\bc#\b': 'C#',
    r'\b\.net\b': '.NET',
    r'\bphp\b': 'PHP',
    r'\bc\+\+\b': 'C++',
    r'\br\b': 'R',
    r'\bgolang\b': 'GO',
    r'\bkotlin\b': 'KOTLIN',
    r'\bbash\b': 'BASH/SHELL',

    # Backend & Frameworks
    r'\bdjango\b': 'DJANGO',
    r'\bflask\b': 'FLASK',
    r'\bfastapi\b': 'FASTAPI',
    r'\bspring\b': 'SPRING BOOT',
    r'\blaravel\b': 'LARAVEL',
    r'\bnode\.?js\b': 'NODE.JS',
    r'\bexpress\b': 'EXPRESS.JS',

    # Frontend
    r'\breact\b': 'REACT',
    r'\bangular\b': 'ANGULAR',
    r'\bvue\b': 'VUE.JS',
    r'\bhtml\b': 'HTML',
    r'\bcss\b': 'CSS',
    r'\btailwind\b': 'TAILWIND',
    r'\bbootstrap\b': 'BOOTSTRAP',

    # Datos
    r'\bsql\b': 'SQL',
    r'\bmysql\b': 'MYSQL',
    r'\bpostgres': 'POSTGRESQL',
    r'\bsql server\b': 'SQL SERVER',
    r'\bmongo': 'MONGODB',
    r'\bpandas\b': 'PANDAS',
    r'\bnumpy\b': 'NUMPY',
    r'\bpower bi\b': 'POWER BI',
    r'\btableau\b': 'TABLEAU',
    r'\bexcel\b': 'EXCEL',

    # Cloud & Infra
    r'\baws\b': 'AWS',
    r'\bamazon web services\b': 'AWS',
    r'\bazure\b': 'AZURE',
    r'\bgcp\b': 'GOOGLE CLOUD',
    r'\bgoogle cloud\b': 'GOOGLE CLOUD',
    r'\bdocker\b': 'DOCKER',
    r'\bkubernetes\b': 'KUBERNETES',
    r'\bjenkins\b': 'JENKINS',
    r'\bgit\b': 'GIT',
    r'\blinux\b': 'LINUX',
    r'\bubuntu\b': 'UBUNTU',
    r'\bzoho\b': 'ZOHO CRM'

    # Ciberseguridad & Redes
    r'\bkali\b': 'KALI LINUX',
    r'\bwireshark\b': 'WIRESHARK',
    r'\bcisco\b': 'CISCO',
    r'\bccna\b': 'CCNA',
    r'\bfirewall\b': 'FIREWALL',
    r'\bowasp\b': 'OWASP',
    r'\biso 27001\b': 'ISO 27001'
}

def extraer_skills(texto):
    """Busca palabras clave dentro del texto sucio usando Regex."""
    if not isinstance(texto, str): return []
    texto_lower = texto.lower()
    skills = set()
    for patron, tech in MAPA_TECNOLOGIAS.items():
        if re.search(patron, texto_lower):
            skills.add(tech)
    return list(skills)

def limpiar_datos_universal():
    print("🧹 INICIANDO PROTOCOLO DE LIMPIEZA PROFUNDA...")
    
    data_final = []
    ids_vistos = set()
    total_basura = 0

    # ---------------------------------------------------------
    # 1. PROCESAR JOOBLE (JSON con 'raw_text')
    # ---------------------------------------------------------
    archivo_jooble = "data_cruda_jooble.json"
    if os.path.exists(archivo_jooble):
        try:
            with open(archivo_jooble, "r", encoding="utf-8") as f:
                datos_jooble = json.load(f)
            print(f"📥 Jooble: Analizando {len(datos_jooble)} registros crudos...")
            
            for item in datos_jooble:
                link = item.get("link", "")
                
                # Evitar duplicados
                if link in ids_vistos: continue
                
                # Datos Crudos
                titulo = item.get("titulo", "Sin Título")
                raw_text = item.get("raw_text", "") # Aquí está TODO el texto
                
                # --- A. EXTRACCIÓN DE SKILLS ---
                # Buscamos skills en TODO el texto (título + descripción)
                skills_detectadas = extraer_skills(raw_text)
                
                # --- B. FILTRO DE CALIDAD ---
                # Si no encontramos skills, verificamos si el título al menos suena tech
                palabras_clave_titulo = ["desarrollador", "programador", "sistemas", "analista", "datos", "data", "software", "web", "tech", "informatica", "redes", "seguridad"]
                es_titulo_tech = any(p in titulo.lower() for p in palabras_clave_titulo)
                
                # Si NO tiene skills Y NO parece título de sistemas -> BASURA
                if not skills_detectadas and not es_titulo_tech:
                    total_basura += 1
                    continue 

                # --- C. EXTRACCIÓN DE SALARIO ---
                # Buscamos líneas que tengan "$" en el texto crudo
                salario = "No especificado"
                if "$" in raw_text:
                    for linea in raw_text.split('\n'):
                        if "$" in linea and len(linea) < 40: # Evitamos frases largas
                            salario = linea.strip()
                            break
                
                # --- D. EXTRACCIÓN DE UBICACIÓN ---
                ubicacion = "Quito" # Default
                if "Remoto" in raw_text: ubicacion = "Remoto"
                elif "Híbrido" in raw_text: ubicacion = "Híbrido"

                # Guardamos registro limpio
                registro = {
                    "fuente": "Jooble",
                    "fecha": item.get("fecha_recoleccion", datetime.now().strftime("%Y-%m-%d")),
                    "titulo": titulo,
                    "empresa": "Confidencial/Ver Link",
                    "ubicacion": ubicacion,
                    "salario": salario,
                    "skills": sorted(skills_detectadas), # Ordenaditas A-Z
                    "link": link
                }
                data_final.append(registro)
                ids_vistos.add(link)
                
        except Exception as e:
            print(f"⚠️ Error leyendo Jooble: {e}")

    # ---------------------------------------------------------
    # 2. PROCESAR COMPUTRABAJO (CSV de tu amigo) - Opcional
    # ---------------------------------------------------------
    archivo_csv = "ofertas_crudas.csv"
    if os.path.exists(archivo_csv):
        try:
            df_compu = pd.read_csv(archivo_csv)
            print(f"📥 Computrabajo: Integrando {len(df_compu)} registros...")
            
            for _, row in df_compu.iterrows():
                link = row.get("url_publicacion", "")
                if link in ids_vistos: continue
                
                titulo_limpio = str(row.get("oferta_laboral", "")).replace("PostuladoVista", "").strip()
                
                # Aquí solo podemos buscar skills en el título (porque no hay descripción)
                skills_detectadas = extraer_skills(titulo_limpio)
                
                registro = {
                    "fuente": "Computrabajo",
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "titulo": titulo_limpio,
                    "empresa": str(row.get("compania", "Confidencial")),
                    "ubicacion": "Quito",
                    "salario": str(row.get("sueldo", "No especificado")),
                    "skills": sorted(skills_detectadas),
                    "link": link
                }
                data_final.append(registro)
                ids_vistos.add(link)
        except: pass

    # ---------------------------------------------------------
    # 3. GUARDADO FINAL
    # ---------------------------------------------------------
    print("-" * 40)
    print(f"📊 RESULTADOS:")
    print(f"   ✅ Ofertas Válidas: {len(data_final)}")
    print(f"   🗑️ Basura Eliminada: {total_basura}")
    
    if data_final:
        # Guardar JSON Maestro
        with open("base_datos_maestra.json", "w", encoding="utf-8") as f:
            json.dump(data_final, f, indent=4, ensure_ascii=False)
            
        # Guardar Excel
        df = pd.DataFrame(data_final)
        # Convertir lista de skills a texto bonito "Python, SQL"
        df['skills'] = df['skills'].apply(lambda x: ", ".join(x))
        
        df.to_excel("REPORTE_OFICIAL_FINAL.xlsx", index=False)
        print(f"💾 Archivo generado: 'REPORTE_OFICIAL_FINAL.xlsx'")
    else:
        print("⚠️ No hay datos para guardar.")

if __name__ == "__main__":
    limpiar_datos_universal()