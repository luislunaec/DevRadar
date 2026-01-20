import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json
import time
import random
import os 

# --- CONFIGURACIÓN ---
PERFILES_A_BUSCAR = [
    "programador", "desarrollador backend", "desarrollador frontend", 
    "especialista ciberseguridad", "ingeniero de datos", 
    "administrador de redes", "devops", "qa tester"
]

def recolector_fuerza_bruta():
    print("INICIANDO RECOLECTOR MASIVO DE DATOS")
    
    nombre_archivo = "data_cruda_jooble.json"
    lista_ofertas_acumulada = []
    links_vistos = set()
    
    # 1. Cargar memoria previa
    if os.path.exists(nombre_archivo):
        try:
            with open(nombre_archivo, "r", encoding="utf-8") as f:
                lista_ofertas_acumulada = json.load(f)
            for o in lista_ofertas_acumulada: links_vistos.add(o.get("link"))
            print(f"📚 Memoria cargada: {len(links_vistos)} ofertas previas.")
        except: pass

    # 2. Navegador (CONFIGURACIÓN BLINDADA) 🛡️
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-popup-blocking") # Bloquear popups molestos
    options.add_argument("--no-sandbox") # Evita crasheos en ciertos sistemas
    options.add_argument("--disable-dev-shm-usage") # Usa mejor la memoria
    
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
                time.sleep(2) # Pausa para que respire
                
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

                            lista_ofertas_acumulada.append({
                                "link": link,
                                "titulo": titulo,
                                "raw_text": texto_crudo, 
                                "fecha_recoleccion": time.strftime("%Y-%m-%d")
                            })
                            
                            nuevos += 1
                            ofertas_perfil += 1
                    except: pass
                
                print(f"   ⬇️ Bajando... (Total BD: {len(lista_ofertas_acumulada)})")
                
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
            
            # Guardado rápido
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                json.dump(lista_ofertas_acumulada, f, indent=4, ensure_ascii=False)

    except Exception as e: 
        print(f"❌ Error CRÍTICO durante la ejecución: {e}")
    finally: 
        try: driver.quit()
        except: pass
        print("🏁 Fin.")

if __name__ == "__main__":
    recolector_fuerza_bruta()