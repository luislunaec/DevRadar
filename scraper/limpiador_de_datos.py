import json
import unicodedata
import re

# --- NIVEL 1: PALABRAS VIP (Entran directo) ---
TECH_VIP = [
    "programador", "desarrollador", "developer", "backend", "frontend", "fullstack", 
    "devops", "java", "python", "php", "sql", "net", "react", "angular", "node", 
    "aws", "azure", "linux", "scrum", "agile", "ciberseguridad", "cyber", "robotica", 
    "machine learning", "ia", "ai", "tester", "qa", "data scientist", "data engineer"
]

# --- NIVEL 2: ROLES GENÉRICOS ---
ROLES_GENERICOS = [
    "analista", "ingeniero", "tecnico", "técnico", "consultor", "arquitecto", 
    "coordinador", "jefe", "gerente", "lider", "especialista", "administrador",
    "pasante", "practicante", "trainee", "asistente", "soporte", "help desk", "docente", "tutor"
]

# --- APELLIDOS OBLIGATORIOS (Si es genérico, DEBE tener uno de estos) ---
APELLIDOS_TECH = [
    "sistemas", "software", "informatica", "informática", "computacion", "computación",
    "tecnologia", "technology", "ti", "it", "datos", "data", "redes", "networking",
    "web", "aplicaciones", "app", "cloud", "nube", "digital", "automatizacion", 
    "programming", "engineering"
]

# --- NIVEL 3: BASURA (Si tiene esto, SE VA) ---
BASURA = [
    "chofer", "conductor", "vendedor", "cajero", "limpieza", "guardia", "recepcionista",
    "call center", "bodega", "almacen", "odontolog", "abogado", "contador", "financier", 
    "credito", "cobranza", "recursos humanos", "rrhh", "marketing", "comercial", "ventas", 
    "automotriz", "mecanico", "electrico", "civil", "obra", "hotel", "turismo", "restaurante",
    "enfermer", "medico", "cocin", "panader", "secretaria", "administrativo", "administrativa", 
    "contable", "atencion al cliente", "cliente", "talento humano"
]

def normalizar(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if unicodedata.category(c) != 'Mn')

def tiene_palabra_completa(lista_palabras, texto):
    """ Busca palabra exacta usando Regex (Ej: evita que 'ti' coincida con 'tiempo') """
    for palabra in lista_palabras:
        # \b significa límite de palabra
        if re.search(r'\b' + re.escape(palabra) + r'\b', texto):
            return True, palabra
    return False, None

def ejecutar_filtro_corregido():
    print("🧠 EJECUTANDO FILTRO CONTEXTUAL V2 (Estricto)...")
    
    try:
        with open("base_datos_masiva.json", "r", encoding="utf-8") as f:
            todas = json.load(f)
    except:
        print("❌ Error: No existe 'base_datos_masiva.json'")
        return

    validas = []
    eliminadas = 0

    print(f"📊 Analizando {len(todas)} ofertas...\n")

    for oferta in todas:
        titulo = normalizar(oferta.get("titulo", ""))
        titulo_orig = oferta.get("titulo", "")
        
        # 1. FILTRO DE BASURA (Prioridad Máxima)
        es_basura, palabra_basura = tiene_palabra_completa(BASURA, titulo)
        if es_basura:
            eliminadas += 1
            # print(f"🗑️ Basura detectada ({palabra_basura}): {titulo_orig}")
            continue

        razon_aprobacion = ""

        # 2. CHEQUEO VIP (Nivel 1)
        es_vip, palabra_vip = tiene_palabra_completa(TECH_VIP, titulo)
        if es_vip:
            razon_aprobacion = f"VIP ({palabra_vip})"
        
        # 3. CHEQUEO CONTEXTUAL (Nivel 2)
        if not razon_aprobacion:
            es_rol_gen, _ = tiene_palabra_completa(ROLES_GENERICOS, titulo)
            es_apellido_tech, apellido = tiene_palabra_completa(APELLIDOS_TECH, titulo)
            
            if es_rol_gen and es_apellido_tech:
                razon_aprobacion = f"Rol + Tech ({apellido})"
            elif es_apellido_tech:
                # Caso: "Jefe de Sistemas" o simplemente "Sistemas"
                razon_aprobacion = f"Tech Fuerte ({apellido})"

        # DECISIÓN FINAL
        if razon_aprobacion:
            validas.append(oferta)
        else:
            eliminadas += 1

    # RE-INDEXAR
    for i, oferta in enumerate(validas):
        oferta["id"] = i + 1

    print("-" * 30)
    print(f"✅ Ofertas Aprobadas: {len(validas)}")
    print(f"🗑️ Ofertas Eliminadas: {eliminadas}")
    print("-" * 30)
    
    with open("base_datos_filtrada.json", "w", encoding="utf-8") as f:
        json.dump(validas, f, indent=4, ensure_ascii=False)
    print("💾 Guardado en: 'base_datos_filtrada.json'")

if __name__ == "__main__":
    ejecutar_filtro_corregido()