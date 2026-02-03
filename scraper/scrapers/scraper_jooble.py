import os
import sys
import time
import pandas as pd
import random  # <--- ¡¡AGREGA ESTA LÍNEA QUE FALTABA!! 🎲
from datetime import datetime, timedelta
import re
# ... el resto sigue igual

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

# Permitir imports desde root
_scraper_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scraper_root not in sys.path:
    sys.path.insert(0, _scraper_root)

from db.supabase_helper import guardar_oferta_cruda

# Importar pantalla virtual para servidores Linux (VPS)
try:
    from pyvirtualdisplay import Display
except ImportError:
    pass

class RecolectorJooble:
    """
    Scraper de Jooble estandarizado (Clase).
    Misma lógica blindada de Selenium, pero estructura compatible con Main.
    """

    def __init__(self, roles, scrape_days: int = 30):
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
        # self.options.add_argument("--headless") # ¡OJO! En Jooble a veces headless falla, mejor Xvfb

    def _jooble_date_param(self) -> str | None:
        """
        Mapea los días a los parámetros de URL de Jooble.
        """
        if self.scrape_days <= 1: return "8" # Últimas 24 horas
        if self.scrape_days <= 3: return "2" # Últimos 3 días
        if self.scrape_days <= 7: return "3" # Últimos 7 días
        return None # Sin parámetro = Cualquier fecha (Histórico completo)

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
        print(f"🚀 INICIANDO RECOLECTOR JOOBLE (MAX HISTÓRICO)")
        
        # --- BLOQUE VPS: PANTALLA FANTASMA (Solo en Linux) ---
        display = None
        if sys.platform.startswith('linux'):
            try:
                print("🐧 Detectado Linux: Iniciando Pantalla Virtual...")
                display = Display(visible=0, size=(1920, 1080))
                display.start()
            except Exception as e:
                print(f"⚠️ No se pudo iniciar Xvfb: {e}")
        # -----------------------------------------------------

        date_param = self._jooble_date_param()
        
        # Fix versión 144 / Driver
        driver = None
        try:
            driver = uc.Chrome(options=self.options, version_main=144)
        except:
            print("⚠️ Versión 144 falló, intentando automático...")
            try:
                driver = uc.Chrome(options=self.options)
            except Exception as e:
                print(f"❌ Error fatal iniciando Chrome: {e}")
                if display: display.stop()
                return

        try:
            for rol in self.roles:
                print(f"\n🔎 --- BUSCANDO: {rol.upper()} ---")
                
                base = "https://ec.jooble.org/SearchResult?"
                # 'ukw' es la keyword, 'rgns' es la región (Quito por defecto, o quitar para todo Ecuador)
                query = f"ukw={rol.replace(' ', '%20')}" 
                url = f"{base}date={date_param}&{query}" if date_param else f"{base}{query}"
                
                driver.get(url)
                time.sleep(random.uniform(3, 5))
                
                contador_rol = 0
                intentos_sin_nuevos = 0
                links_vistos = set()
                
                # AUMENTADO: Ahora busca hasta 200 por rol (antes 50)
                while contador_rol < 200:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2.5) # Un pelín más lento para dar tiempo a cargar
                    
                    # Selectores de Jooble (cambian a veces)
                    tarjetas = driver.find_elements(By.CSS_SELECTOR, "article")
                    if not tarjetas: tarjetas = driver.find_elements(By.CSS_SELECTOR, "div[data-test-name='_jobCard']")
                    
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

                            # 2. TÍTULO
                            titulo = "Sin Título"
                            try: titulo = tarjeta.find_element(By.TAG_NAME, "h2").text
                            except: pass
                            
                            titulo = titulo.replace("\n", " ").strip() if titulo else "Sin Título"

                            # 3. TEXTO
                            texto_full = tarjeta.get_attribute("innerText")
                            if not texto_full or len(texto_full) < 10:
                                texto_full = tarjeta.text

                            # Extracciones
                            sueldo_detectado = self.extraer_sueldo_numerico(texto_full)
                            locacion_detectada = self.extraer_ubicacion(texto_full)
                            
                            # Guardar en memoria
                            self.datos.append({
                                'plataforma': 'jooble',
                                'rol_busqueda': rol,
                                'fecha_publicacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # Jooble no da fecha exacta fácil
                                'oferta_laboral': titulo,
                                'locacion': locacion_detectada,
                                'descripcion': texto_full,
                                'sueldo': sueldo_detectado,
                                'compania': 'Confidencial',
                                'url_publicacion': link
                            })

                            contador_rol += 1
                            nuevos_ciclo += 1
                            if nuevos_ciclo % 10 == 0:
                                print(f"   ⚡ {contador_rol} ofertas recolectadas...")

                        except: continue
                    
                    # Si no aparecen nuevos tras scroll, intentamos 3 veces y salimos
                    if nuevos_ciclo == 0:
                        intentos_sin_nuevos += 1
                        if intentos_sin_nuevos >= 3: 
                            print("   🚫 No cargan más ofertas. Fin del rol.")
                            break
                    else:
                        intentos_sin_nuevos = 0

                self.registros_por_rol[rol] = contador_rol
                print(f"   🏆 Total '{rol}': {contador_rol}")

        except Exception as e:
            print(f"❌ Error crítico en recolección: {e}")
        finally:
            if driver:
                try: driver.quit()
                except: pass
            if display:
                try: display.stop()
                except: pass
            
            # Guardar al final
            self.guardar_supabase()

    def guardar_supabase(self):
        """Guarda todo lo recolectado de una sola vez al final"""
        if not self.datos: 
            print("\n⚠️ No se recolectaron datos para guardar.")
            return

        df = pd.DataFrame(self.datos)
        # Limpiar duplicados de URL
        df.drop_duplicates(subset=['url_publicacion'], inplace=True)
        print(f"\n💾 Guardando {len(df)} ofertas únicas en Supabase (jobs_raw)...")

        exitos = 0
        errores = 0
        for _, row in df.iterrows():
            datos_fila = row.to_dict()
            # Validar que sueldo sea None si no existe (Supabase no acepta NaN de pandas)
            if pd.isna(datos_fila.get('sueldo')): datos_fila['sueldo'] = None
            
            if guardar_oferta_cruda(datos_fila):
                exitos += 1
            else:
                errores += 1
            time.sleep(0.01) # Micro pausa
            
        print(f"✅ FINALIZADO: {exitos} guardados. ({errores} errores).")

# =============================================================================
# 🏁 EJECUCIÓN MANUAL (PRUEBAS)
# =============================================================================
if __name__ == "__main__":
    # Roles de prueba locales
    ROLES_TEST = ["programador", "analista de datos"]
    
    # 60 días = Sin filtro de fecha (trae todo)
    bot = RecolectorJooble(ROLES_TEST, scrape_days=60)
    bot.recolectar()