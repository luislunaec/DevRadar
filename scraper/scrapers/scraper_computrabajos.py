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
# Permitir imports cuando se ejecuta desde main.py o directamente
_scraper_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scraper_root not in sys.path:
    sys.path.insert(0, _scraper_root)

# Importamos la función real de guardado en base de datos
from db.supabase_helper import guardar_oferta_cruda

class RecolectorComputrabajo:
    """
    Scraper DE PRODUCCIÓN para Computrabajo.
    - Usa 'requests' (rápido).
    - Tiene paginación infinita automática.
    - Guarda directamente en Supabase.
    """

    def __init__(self, roles, scrape_days: int = 30):
        self.base_url = "https://ec.computrabajo.com"
        self.roles = roles  # Recibe la lista del Main
        self.scrape_days = scrape_days
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

        if 'hace más de 30 días' in texto or 'hace mas de 30 días' in texto:
            return (ahora - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

        meses = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }

        match_fecha = re.search(r'(\d+)\s+de\s+(\w+)', texto)
        if match_fecha:
            dia = int(match_fecha.group(1))
            mes_texto = match_fecha.group(2).lower()
            if mes_texto in meses:
                mes = meses[mes_texto]
                anio = ahora.year - 1 if mes > ahora.month else ahora.year
                try:
                    return datetime(anio, mes, dia).strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return ''
        return ''

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
        """
        Recorre TODAS las páginas disponibles para cada rol en la lista.
        """
        for rol in self.roles:
            print(f"\n{'=' * 60}")
            print(f"🔎 BUSCANDO EN COMPUTRABAJO: {rol.upper()}")
            print(f"{'=' * 60}")

            slug = rol.replace(" ", "-")
            contador_rol = 0
            pagina_actual = 1
            max_paginas_seguridad = 60 # 🛑 Límite de seguridad para no entrar en loop infinito

            while pagina_actual <= max_paginas_seguridad:
                url = f"{self.base_url}/trabajo-de-{slug}?pubdate={self.scrape_days}&p={pagina_actual}"
                
                try:
                    # Pequeña pausa para no ser bloqueados
                    time.sleep(random.uniform(2, 4))
                    
                    print(f"   📡 Solicitando Pág {pagina_actual}...", end=" ")
                    res = requests.get(url, headers=self.headers, timeout=10)
                    
                    if res.status_code != 200: 
                        print(f"❌ Error HTTP {res.status_code}. Deteniendo rol.")
                        break

                    soup = BeautifulSoup(res.content, 'html.parser')
                    
                    # Verificar si hay alerta de "No hay ofertas"
                    no_ofertas = soup.find('div', string=re.compile("No se ha encontrado ofertas"))
                    if no_ofertas:
                        print("🚫 Fin de resultados (Mensaje web).")
                        break

                    ofertas = soup.find_all('article', class_='box_offer') or soup.find_all('article')

                    if not ofertas:
                        print(f"🚫 0 ofertas encontradas. Fin del camino.")
                        break

                    print(f"✅ {len(ofertas)} ofertas.")

                    # PROCESAMIENTO DE OFERTAS
                    ofertas_nuevas_en_pagina = 0
                    for oferta in ofertas:
                        titulo_tag = oferta.find('h1') or oferta.find('a', recursive=True)
                        if not titulo_tag: continue

                        anchor = titulo_tag.find('a') if titulo_tag.name == 'h1' else titulo_tag
                        href = anchor['href'] if anchor and anchor.has_attr('href') else None
                        if not href: continue
                        link = self.base_url + href

                        raw_title = titulo_tag.get_text(strip=True)
                        oferta_laboral = raw_title.replace('PostuladoVista', '').strip()

                        # --- Extracción de Datos ---
                        parrafos = oferta.find_all('p')
                        locacion = 'Ecuador'
                        if len(parrafos) > 1:
                            loc_candidata = parrafos[1].get_text(strip=True)
                            if "días" not in loc_candidata.lower() and "hoy" not in loc_candidata.lower():
                                locacion = loc_candidata

                        compania = 'N/A'
                        p_fs16 = oferta.find('p', class_='fs16')
                        if p_fs16:
                            compania = p_fs16.get_text(strip=True).split(' - ', 1)[0].strip()

                        sueldo_texto = 'No especificado'
                        info_extras = oferta.find_all('span', class_='mr10')
                        for info in info_extras:
                            if '$' in info.get_text():
                                sueldo_texto = info.get_text(strip=True)
                                break

                        sueldo_numerico = self.extraer_sueldo_numerico(sueldo_texto)
                        
                        # Pausa micro para detalle (opcional)
                        fecha_texto, descripcion = self.parse_detalle(link)
                        fecha_calculada = self.parsear_fecha(fecha_texto) if fecha_texto else ''

                        self.datos.append({
                            'plataforma': 'computrabajo',
                            'rol_busqueda': rol,
                            'fecha_publicacion': fecha_calculada,
                            'oferta_laboral': oferta_laboral,
                            'locacion': locacion,
                            'descripcion': descripcion,
                            'sueldo': sueldo_numerico,
                            'compania': compania,
                            'url_publicacion': link,
                        })

                        contador_rol += 1
                        ofertas_nuevas_en_pagina += 1

                    # Si encontramos ofertas, pasamos a la siguiente página
                    if ofertas_nuevas_en_pagina > 0:
                        pagina_actual += 1
                    else:
                        print("   ⚠️ Página vacía o sin datos válidos. Terminando rol.")
                        break

                except Exception as e:
                    print(f"\n   💥 Error crítico en p.{pagina_actual}: {e}")
                    break

            self.registros_por_rol[rol] = contador_rol
            print(f"   🏆 Total '{rol}': {contador_rol} registros recolectados.")

        # FINALMENTE: GUARDAR TODO EN SUPABASE
        self.guardar_supabase()
        self.mostrar_resumen()

    def parse_detalle(self, url):
        try:
            # Random delay para no quemar la IP
            time.sleep(random.uniform(0.1, 0.5)) 
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
                listas = box_desc.find_all('ul')
                for ul in listas:
                    partes.append("\nRequerimientos:")
                    partes.extend([f"- {li.get_text(strip=True)}" for li in ul.find_all('li')])
                descripcion_str = "\n\n".join(partes)

            return fecha, descripcion_str
        except:
            return '', ''

    def mostrar_resumen(self):
        print(f"\n{'=' * 60}")
        print("RESUMEN DE RECOLECCIÓN COMPUTRABAJO")
        print(f"{'=' * 60}\n")
        roles_ordenados = sorted(self.registros_por_rol.items(), key=lambda x: x[1], reverse=True)
        for i, (rol, cantidad) in enumerate(roles_ordenados, 1):
            print(f"{i:2}. {rol:30} → {cantidad:4} registros")
        total = sum(self.registros_por_rol.values())
        print(f"\n{'=' * 60}")
        print(f"TOTAL DE REGISTROS (con duplicados): {total}")
        print(f"{'=' * 60}\n")

    def guardar_supabase(self):
        """
        Limpia duplicados y envía a Supabase (jobs_raw).
        """
        df = pd.DataFrame(self.datos)
        print(f"\n💾 Procesando {len(df)} registros para Supabase...")
        
        if not df.empty:
            # Eliminar duplicados exactos de URL antes de subir
            df.drop_duplicates(subset=['url_publicacion'], inplace=True)
            print(f"   ↳ {len(df)} registros únicos listos para subir.")

            exitos = 0
            errores = 0
            
            for _, row in df.iterrows():
                datos = {
                    'plataforma': row.get('plataforma', 'computrabajo'),
                    'rol_busqueda': row.get('rol_busqueda', ''),
                    'fecha_publicacion': row.get('fecha_publicacion', ''),
                    'oferta_laboral': row.get('oferta_laboral', 'Sin Título'),
                    'locacion': row.get('locacion', 'Ecuador'),
                    'descripcion': row.get('descripcion', ''),
                    'sueldo': row.get('sueldo'),
                    'compania': row.get('compania', 'Confidencial'),
                    'url_publicacion': row.get('url_publicacion', '')
                }
                
                # LLAMADA A LA BASE DE DATOS
                if guardar_oferta_cruda(datos):
                    exitos += 1
                else:
                    errores += 1
                
                # Pausa mínima para no saturar la API
                time.sleep(0.01)
            
            print(f"\n✅ SUBIDA COMPLETA: {exitos} guardados exitosamente.")
            if errores > 0:
                print(f"⚠️ {errores} errores al guardar.")
        else:
            print("\n⚠️ No hay datos para guardar.")