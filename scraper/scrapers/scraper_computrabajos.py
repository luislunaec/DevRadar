import os
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime, timedelta
import re

# =============================================================================
# 🔗 CONFIGURACIÓN DE RUTAS E IMPORTACIONES
# =============================================================================
_scraper_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scraper_root not in sys.path:
    sys.path.insert(0, _scraper_root)

from db.supabase_helper import guardar_oferta_cruda

class RecolectorComputrabajo:
    """
    Scraper optimizado para ejecución diaria en Contabo.
    """

    def __init__(self, roles, scrape_days: int = 2):
        self.base_url = "https://ec.computrabajo.com"
        self.roles = roles
        self.scrape_days = scrape_days # Ahora controlado desde el main (ej: 2 días)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.datos = []
        self.registros_por_rol = {}

    def parsear_fecha(self, texto_fecha):
        ahora = datetime.now()
        texto = texto_fecha.lower().strip()
        texto = texto.replace('(actualizada)', '').strip()

        match_horas = re.search(r'hace\s+(\d+)\s+horas?', texto)
        if match_horas:
            horas = int(match_horas.group(1))
            return (ahora - timedelta(hours=horas)).strftime('%Y-%m-%d %H:%M:%S')

        match_dias = re.search(r'hace\s+(\d+)\s+días?', texto)
        if match_dias:
            dias = int(match_dias.group(1))
            return (ahora - timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')

        return ahora.strftime('%Y-%m-%d %H:%M:%S')

    def extraer_sueldo_numerico(self, texto_sueldo):
        if 'no especificado' in texto_sueldo.lower():
            return None
        match = re.search(r'([\d.,]+)', texto_sueldo)
        if match:
            numero_texto = match.group(1).replace('.', '').replace(',', '.')
            try:
                return float(numero_texto)
            except ValueError:
                return None
        return None

    def recolectar(self):
        for rol in self.roles:
            print(f"\n🔎 BUSCANDO EN COMPUTRABAJO: {rol.upper()} (Últimos {self.scrape_days} días)")
            
            slug = rol.replace(" ", "-")
            contador_rol = 0
            pagina_actual = 1
            max_paginas_seguridad = 20 # Reducido para diario, usualmente sobran

            while pagina_actual <= max_paginas_seguridad:
                # pubdate={self.scrape_days} filtra directamente en el servidor de Computrabajo
                url = f"{self.base_url}/trabajo-de-{slug}?pubdate={self.scrape_days}&p={pagina_actual}"
                
                try:
                    time.sleep(random.uniform(2, 4))
                    print(f"   📡 Pág {pagina_actual}...", end=" ")
                    res = requests.get(url, headers=self.headers, timeout=10)
                    
                    if res.status_code != 200: break

                    soup = BeautifulSoup(res.content, 'html.parser')
                    no_ofertas = soup.find('div', string=re.compile("No se ha encontrado ofertas"))
                    if no_ofertas: break

                    ofertas = soup.find_all('article', class_='box_offer') or soup.find_all('article')
                    if not ofertas: break

                    print(f"✅ {len(ofertas)} ofertas.")

                    for oferta in ofertas:
                        titulo_tag = oferta.find('h1') or oferta.find('a', recursive=True)
                        if not titulo_tag: continue

                        anchor = titulo_tag.find('a') if titulo_tag.name == 'h1' else titulo_tag
                        href = anchor['href'] if anchor and anchor.has_attr('href') else None
                        if not href: continue
                        link = self.base_url + href

                        raw_title = titulo_tag.get_text(strip=True)
                        oferta_laboral = raw_title.replace('PostuladoVista', '').strip()

                        # Locación y Compañía
                        parrafos = oferta.find_all('p')
                        locacion = 'Ecuador'
                        if len(parrafos) > 1:
                            loc_candidata = parrafos[1].get_text(strip=True)
                            if "días" not in loc_candidata.lower() and "hoy" not in loc_candidata.lower():
                                locacion = loc_candidata

                        compania = 'Confidencial'
                        p_fs16 = oferta.find('p', class_='fs16')
                        if p_fs16:
                            compania = p_fs16.get_text(strip=True).split(' - ', 1)[0].strip()

                        # Sueldo
                        sueldo_texto = 'No especificado'
                        info_extras = oferta.find_all('span', class_='mr10')
                        for info in info_extras:
                            if '$' in info.get_text():
                                sueldo_texto = info.get_text(strip=True)
                                break

                        fecha_texto, descripcion = self.parse_detalle(link)
                        fecha_calculada = self.parsear_fecha(fecha_texto)

                        self.datos.append({
                            'plataforma': 'computrabajo',
                            'rol_busqueda': rol,
                            'fecha_publicacion': fecha_calculada,
                            'oferta_laboral': oferta_laboral,
                            'locacion': locacion,
                            'descripcion': descripcion,
                            'sueldo': self.extraer_sueldo_numerico(sueldo_texto),
                            'compania': compania,
                            'url_publicacion': link,
                            'processed': False # Se marca como pendiente para el Limpiador
                        })

                        contador_rol += 1
                    pagina_actual += 1

                except Exception as e:
                    print(f"\n   💥 Error en p.{pagina_actual}: {e}")
                    break

            self.registros_por_rol[rol] = contador_rol

        self.guardar_supabase()

    def parse_detalle(self, url):
        try:
            res = requests.get(url, headers=self.headers, timeout=5)
            if res.status_code != 200: return '', ''
            soup = BeautifulSoup(res.content, 'html.parser')

            fecha = ''
            elementos_fs13 = soup.find_all('p', class_='fs13')
            for el in elementos_fs13:
                txt = el.get_text(strip=True)
                if "Publicado" in txt or "hace" in txt.lower():
                    fecha = txt
                    break

            descripcion_str = ''
            box_desc = soup.find('div', class_='mb40 pb40 bb1')
            if box_desc:
                partes = [p.get_text(strip=True) for p in box_desc.find_all('p')]
                descripcion_str = "\n\n".join(partes)

            return fecha, descripcion_str
        except Exception:
            return "", ""

    def guardar_supabase(self):
        df = pd.DataFrame(self.datos)
        if df.empty: return

        df.drop_duplicates(subset=['url_publicacion'], inplace=True)
        print(f"\n💾 Subiendo {len(df)} registros únicos a jobs_raw...")

        exitos = 0
        for _, row in df.iterrows():
            # El helper debe usar UPSERT basado en 'url_publicacion'
            if guardar_oferta_cruda(row.to_dict()):
                exitos += 1
        
        print(f"✅ Proceso terminado: {exitos} guardados/actualizados.")

# Función para ser llamada desde main.py
def correr_scraper_computrabajo(roles, dias=2):
    recolector = RecolectorComputrabajo(roles=roles, scrape_days=dias)
    recolector.recolectar()