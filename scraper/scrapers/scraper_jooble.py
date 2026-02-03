import os
import sys
import time
import pandas as pd
from datetime import datetime, timedelta
import re

# --- IMPORTS DE SELENIUM ---
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Permitir imports desde root
_scraper_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scraper_root not in sys.path:
    sys.path.insert(0, _scraper_root)

from db.supabase_helper import guardar_oferta_cruda

# Esta lista se usa si lo ejecutas manual, pero el main.py le pasará la suya
ROLES_A_BUSCAR = [
    "programador", "desarrollador software", "python developer", 
    "java developer", "data analyst", "qa automation"
]

class RecolectorJooble:
    """
    Scraper de Jooble estandarizado (Clase).
    Misma lógica blindada de Selenium, pero estructura compatible con Main.
    """

    def __init__(self, roles, scrape_days: int = 3):
        self.base_url = "https://ec.jooble.org"
        self.roles = roles
        self.scrape_days = scrape_days
        self.datos = []
        self.registros_por_rol = {}
        
        # Configuración Chrome
        self.options = uc.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-popup-blocking")
        self.options.add_argument("--no-sandbox")

    def _jooble_date_param(self) -> str | None:
        """
        Mapea los días a los parámetros de URL de Jooble.
        Para 30 días, devolvemos None para que traiga todo lo reciente.
        """
        if self.scrape_days <= 1: return "8"
        if self.scrape_days <= 3: return "2"
        if self.scrape_days <= 7: return "3"
        return None

    def extraer_sueldo_numerico(self, texto_tarjeta):
        if not texto_tarjeta: return None
        lineas = texto_tarjeta.split('\n')
        for linea in lineas:
            l = linea.strip()
            if ("$" in l or "USD" in l) and any(char.isdigit() for char in l):
                if len(l) < 50: return l
        return None

    def extraer_ubicacion(self, texto_tarjeta):
        if not texto_tarjeta: return "Ecuador"
        l = texto_tarjeta.lower()
        if "quito" in l: return "Quito"
        if "guayaquil" in l: return "Guayaquil"
        if "cuenca" in l: return "Cuenca"
        if "remoto" in l: return "Remoto"
        return "Ecuador"

    def recolectar(self):
        print(f"🚀 INICIANDO RECOLECTOR JOOBLE (CLASE BLINDADA)")
        date_param = self._jooble_date_param()
        
        # Fix versión 144
        try:
            driver = uc.Chrome(options=self.options, version_main=144)
        except:
            print("⚠️ Versión 144 falló, intentando automático...")
            driver = uc.Chrome(options=self.options)

        try:
            for rol in self.roles:
                print(f"\n🔎 --- BUSCANDO: {rol.upper()} ---")
                
                base = "https://ec.jooble.org/SearchResult?"
                query = f"ukw={rol.replace(' ', '%20')}&rgns=Quito"
                url = f"{base}date={date_param}&{query}" if date_param else f"{base}{query}"
                
                driver.get(url)
                time.sleep(4)
                
                contador_rol = 0
                intentos_sin_nuevos = 0
                links_vistos = set()
                
                # Bucle de scroll limitado
                while contador_rol < 50:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    tarjetas = driver.find_elements(By.CSS_SELECTOR, "article")
                    if not tarjetas: tarjetas = driver.find_elements(By.CSS_SELECTOR, "div[data-test-name='_jobCard']")
                    if not tarjetas: tarjetas = driver.find_elements(By.CSS_SELECTOR, "div[class*='JobCard']")

                    nuevos_ciclo = 0
                    
                    for tarjeta in tarjetas:
                        try:
                            # 1. LINK
                            try:
                                elem_link = tarjeta.find_element(By.TAG_NAME, "a")
                                link = elem_link.get_attribute("href")
                            except: continue

                            if not link or link in links_vistos: continue
                            links_vistos.add(link)

                            # 2. TÍTULO (Lógica H2 -> H1 -> Link)
                            titulo = "Sin Título"
                            try: titulo = tarjeta.find_element(By.TAG_NAME, "h2").text
                            except: pass
                            
                            if not titulo or titulo == "Sin Título":
                                try: titulo = tarjeta.find_element(By.TAG_NAME, "h1").text
                                except: pass
                            
                            if not titulo or titulo == "Sin Título":
                                try: titulo = elem_link.text
                                except: pass

                            titulo = titulo.replace("\n", " ").strip() if titulo else "Sin Título"

                            # 3. TEXTO (InnerText)
                            texto_full = tarjeta.get_attribute("innerText")
                            if not texto_full or len(texto_full) < 10:
                                texto_full = tarjeta.text

                            # Extracciones
                            sueldo_detectado = self.extraer_sueldo_numerico(texto_full)
                            locacion_detectada = self.extraer_ubicacion(texto_full)
                            
                            # Guardamos en lista interna
                            self.datos.append({
                                'plataforma': 'jooble',
                                'rol_busqueda': rol,
                                'fecha_publicacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                'oferta_laboral': titulo,
                                'locacion': locacion_detectada,
                                'descripcion': texto_full,
                                'sueldo': sueldo_detectado,
                                'compania': 'Confidencial',
                                'url_publicacion': link
                            })

                            contador_rol += 1
                            nuevos_ciclo += 1
                            print(f"   ✅ (+1) {titulo[:35]}...")

                        except: continue
                    
                    if nuevos_ciclo == 0:
                        intentos_sin_nuevos += 1
                        if intentos_sin_nuevos >= 3: break
                    else:
                        intentos_sin_nuevos = 0

                self.registros_por_rol[rol] = contador_rol

        except Exception as e:
            print(f"❌ Error crítico: {e}")
        finally:
            try: driver.quit()
            except: pass
            self.guardar_supabase()

    def guardar_supabase(self):
        """Guarda todo lo recolectado de una sola vez al final"""
        if not self.datos: return

        df = pd.DataFrame(self.datos)
        df.drop_duplicates(subset=['url_publicacion'], inplace=True)
        print(f"\n💾 Guardando {len(df)} ofertas únicas en Supabase...")

        exitos = 0
        for _, row in df.iterrows():
            datos_fila = row.to_dict()
            if guardar_oferta_cruda(datos_fila):
                exitos += 1
            time.sleep(0.01)
        print(f"✅ {exitos} ofertas guardadas correctamente.")

if __name__ == "__main__":
    # Esto permite probar el archivo solo
    bot = RecolectorJooble(ROLES_A_BUSCAR, scrape_days=3)
    bot.recolectar()