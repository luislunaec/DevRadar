import os
import sys
import time
import pandas as pd
import random 
from datetime import datetime
import re

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# =============================================================================
# 🔗 CONFIGURACIÓN DE RUTAS E IMPORTACIONES
# =============================================================================
_scraper_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scraper_root not in sys.path:
    sys.path.insert(0, _scraper_root)

from db.supabase_helper import guardar_oferta_cruda

# Pantalla virtual para VPS Linux
try:
    from pyvirtualdisplay import Display
except ImportError:
    pass

class RecolectorJooble:
    """
    Scraper optimizado con Scroll Humano y selectores de alta resistencia.
    Evita el error 'no such window' al no saturar el navegador con comandos rápidos.
    """

    def __init__(self, roles, scrape_days: int = 2):
        self.base_url = "https://ec.jooble.org"
        self.roles = roles
        self.scrape_days = scrape_days 
        self.datos = []
        self.registros_por_rol = {}
        
        self.options = uc.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        # User-agent real para mayor estabilidad
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    def _jooble_date_param(self) -> str | None:
        if self.scrape_days <= 1: return "8" 
        if self.scrape_days <= 3: return "2" 
        if self.scrape_days <= 7: return "3" 
        return None 

    def extraer_sueldo_numerico(self, texto):
        if not texto: return None
        match = re.search(r'\$?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', texto)
        return match.group(0) if match else None

    def extraer_ubicacion(self, texto):
        if not texto: return "Ecuador"
        t = texto.lower()
        if "quito" in t: return "Quito"
        if "guayaquil" in t: return "Guayaquil"
        if "remoto" in t or "teletrabajo" in t: return "Remoto"
        return "Ecuador"

    def recolectar(self):
        print(f"🚀 INICIANDO JOOBLE DIARIO (Mirando {self.scrape_days} días atrás)")
        
        display = None
        if sys.platform.startswith('linux'):
            try:
                display = Display(visible=0, size=(1920, 1080))
                display.start()
            except: pass

        date_param = self._jooble_date_param()
        driver = None
        
        try:
            # Parche de versión 144 para tu Chrome actual
            try:
                driver = uc.Chrome(options=self.options, version_main=144)
            except:
                driver = uc.Chrome(options=self.options)
            
            driver.set_page_load_timeout(35)

            for rol in self.roles:
                print(f"\n🔎 BUSCANDO: {rol.upper()}...")
                query = f"ukw={rol.replace(' ', '%20')}" 
                url = f"{self.base_url}/SearchResult?date={date_param}&{query}" if date_param else f"{self.base_url}/SearchResult?{query}"
                
                try:
                    driver.get(url)
                    time.sleep(random.uniform(5, 8))
                    
                    links_vistos = set()
                    contador_rol = 0
                    
                    # --- SCROLL HUMANO POR TRAMOS ---
                    # Bajamos de 800 en 800 píxeles para que Jooble no nos tumbe la ventana
                    for scroll_step in range(1, 6): 
                        driver.execute_script("window.scrollBy(0, 800);")
                        time.sleep(random.uniform(2.5, 4.0)) 
                        
                        # Selectores basados en data-test-name identificados en inspección
                        tarjetas = driver.find_elements(By.CSS_SELECTOR, 'article, [data-test-name="_jobCard"]')

                        for tarjeta in tarjetas:
                            try:
                                # 1. LINK por atributo de test
                                try:
                                    elem_link = tarjeta.find_element(By.CSS_SELECTOR, "a[data-test-name='_jobCardLink']")
                                    link = elem_link.get_attribute("href")
                                except:
                                    link = tarjeta.find_element(By.TAG_NAME, "a").get_attribute("href")

                                if not link or link in links_vistos: continue
                                links_vistos.add(link)

                                # 2. TÍTULO (Ignorando clases dinámicas como x5dWY-h2)
                                try:
                                    titulo = tarjeta.find_element(By.CSS_SELECTOR, "[data-test-name='_jobCardTitle']").text
                                except:
                                    titulo = "Oferta Tech"

                                texto_full = tarjeta.text

                                # 3. COMPAÑÍA
                                try:
                                    compania = tarjeta.find_element(By.CSS_SELECTOR, "[data-test-name='_jobCardCompanyName']").text
                                except:
                                    compania = "Confidencial"

                                self.datos.append({
                                    'plataforma': 'jooble',
                                    'rol_busqueda': rol,
                                    'fecha_publicacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'oferta_laboral': titulo.strip(),
                                    'locacion': self.extraer_ubicacion(texto_full),
                                    'descripcion': texto_full,
                                    'sueldo': self.extraer_sueldo_numerico(texto_full),
                                    'compania': compania,
                                    'url_publicacion': link
                                })
                                contador_rol += 1
                                
                            except: continue
                except Exception as e:
                    print(f"⚠️ Error cargando rol {rol}: {e}")
                    continue

                self.registros_por_rol[rol] = contador_rol
                print(f"   ✅ Encontradas {contador_rol} ofertas.")

        finally:
            if driver:
                try: driver.quit()
                except: pass
            if display:
                try: display.stop()
                except: pass
            self.guardar_supabase()

    def guardar_supabase(self):
        if not self.datos: return
        df = pd.DataFrame(self.datos).drop_duplicates(subset=['url_publicacion'])
        
        exitos = 0
        for _, row in df.iterrows():
            if guardar_oferta_cruda(row.to_dict()):
                exitos += 1
        print(f"✅ JOOBLE: {exitos} registros en jobs_raw.")

def correr_scraper_jooble(roles, dias=2):
    bot = RecolectorJooble(roles, scrape_days=dias)
    bot.recolectar()