import os
import sys
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
from datetime import datetime
import re

# Permitir imports cuando se ejecuta directamente desde scrapers/
_scraper_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scraper_root not in sys.path:
    sys.path.insert(0, _scraper_root)

from db.supabase_helper import guardar_oferta_cruda

# --- CONFIGURACIÓN ---
PERFILES_A_BUSCAR = [
    "programador"
]

def extraer_salario_simple(texto_tarjeta):
    """
    Busca una línea que tenga dinero ($ o USD) dentro del texto de la tarjeta.
    """
    if not texto_tarjeta: return None
    
    # Dividimos el texto en líneas y revisamos una por una
    lineas = texto_tarjeta.split('\n')
    for linea in lineas:
        # Limpiamos espacios
        l = linea.strip()
        # Si tiene signo de dólar O dice USD, Y ADEMÁS tiene algún número...
        if ("$" in l or "USD" in l) and any(char.isdigit() for char in l):
            # Filtro extra: Que la línea no sea un párrafo gigante (menos de 50 letras)
            if len(l) < 50:
                return l
    return None

def extraer_ubicacion(texto_tarjeta):
    """Extrae la ubicación del texto de la tarjeta"""
    if not texto_tarjeta: return "Ecuador"
    
    lineas = texto_tarjeta.split('\n')
    for linea in lineas:
        l = linea.strip().lower()
        if "quito" in l: return "Quito"
        if "guayaquil" in l: return "Guayaquil"
        if "cuenca" in l: return "Cuenca"
        if "remoto" in l: return "Remoto"
        if "híbrido" in l or "hibrido" in l: return "Híbrido"
    return "Ecuador"

def extraer_empresa(texto_tarjeta):
    """Intenta extraer el nombre de la empresa del texto"""
    if not texto_tarjeta: return "Confidencial"
    
    lineas = texto_tarjeta.split('\n')
    # Generalmente la empresa está en las primeras líneas
    for i, linea in enumerate(lineas[:5]):
        l = linea.strip()
        # Si la línea no tiene números y es razonablemente corta, podría ser la empresa
        if len(l) > 3 and len(l) < 50 and not any(char.isdigit() for char in l):
            if "$" not in l and "USD" not in l and "hace" not in l.lower():
                return l
    return "Confidencial"

def recolector_fuerza_bruta():
    print("INICIANDO RECOLECTOR MASIVO DE DATOS (CON DETECTOR DE SALARIOS)")
    
    links_vistos = set()
    contador_guardados = 0

    # 2. Navegador (CONFIGURACIÓN BLINDADA) 🛡️
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking") 
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage") 
    
    try:
        driver = uc.Chrome(options=options, version_main=143)
    except Exception as e:
        print(f"⚠️ Error al abrir Chrome: {e}")
        print("💡 INTENTO 2: Abriendo sin forzar versión...")
        driver = uc.Chrome(options=options)
    
    try:
        for perfil in PERFILES_A_BUSCAR:
            print(f"\n🔎 --- BUSCANDO: {perfil.upper()} ---")
            driver.get(f"https://ec.jooble.org/SearchResult?ukw={perfil.replace(' ', '%20')}&rgns=Quito")
            
            time.sleep(8)
            
            ofertas_perfil = 0
            sin_novedad = 0
            
            # SCROLL INFINITO HASTA 200
            while ofertas_perfil < 200:
                # Scroll suave
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2) 
                
                try: driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                except: pass
                time.sleep(random.uniform(2, 4))
                
                # Buscamos tarjetas
                tarjetas = driver.find_elements(By.CSS_SELECTOR, "div[data-test-name='_jobCard']")
                if not tarjetas: tarjetas = driver.find_elements(By.TAG_NAME, "article")
                
                nuevos = 0
                for tarjeta in tarjetas:
                    try:
                        # Sacamos el link
                        try:
                            link = tarjeta.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except: continue
                        
                        if link and link not in links_vistos:
                            links_vistos.add(link)
                            
                            # ESTRATEGIA: GUARDAR TODO LO QUE SE VE
                            texto_crudo = tarjeta.text 
                            
                            try: titulo = tarjeta.find_element(By.TAG_NAME, "h2").text
                            except: titulo = "Sin Título"

                            # Extraer información adicional
                            salario_encontrado = extraer_salario_simple(texto_crudo)
                            ubicacion = extraer_ubicacion(texto_crudo)
                            empresa = extraer_empresa(texto_crudo)
                            
                            # Formato estándar requerido
                            datos = {
                                "plataforma": "jooble",
                                "rol_busqueda": perfil if perfil else "",
                                "fecha_publicacion": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "oferta_laboral": titulo if titulo else "Sin Título",
                                "locacion": ubicacion if ubicacion else "Ecuador",
                                "descripcion": texto_crudo if texto_crudo else "",
                                "sueldo": salario_encontrado,  # El helper se encargará de limpiarlo
                                "compania": empresa if empresa else "Confidencial",
                                "url_publicacion": link if link else ""
                            }
                            
                            # Guardar directamente en Supabase
                            if guardar_oferta_cruda(datos):
                                contador_guardados += 1
                            
                            nuevos += 1
                            ofertas_perfil += 1
                    except: pass
                
                print(f"   ⬇️ Bajando... (Total guardados: {contador_guardados})")
                
                if nuevos == 0:
                    sin_novedad += 1
                    if sin_novedad >= 3:
                        try:
                            botones = driver.find_elements(By.TAG_NAME, "button")
                            for b in botones: 
                                if "más" in b.text.lower(): b.click(); time.sleep(2); break
                        except: pass
                    if sin_novedad >= 5: break
                else:
                    sin_novedad = 0

    except Exception as e: 
        print(f"❌ Error CRÍTICO durante la ejecución: {e}")
    finally: 
        try: driver.quit()
        except: pass
        print(f"🏁 Fin. Total ofertas guardadas en Supabase: {contador_guardados}")

if __name__ == "__main__":
    recolector_fuerza_bruta()
