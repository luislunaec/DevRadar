import os
import sys
import pandas as pd
from jobspy import scrape_jobs
import requests
from bs4 import BeautifulSoup
import time
import random
import re
from datetime import datetime

# =============================================================================
# 🔗 CONFIGURACIÓN DE RUTAS E IMPORTACIONES
# =============================================================================
_scraper_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _scraper_root not in sys.path:
    sys.path.insert(0, _scraper_root)

from db.supabase_helper import guardar_oferta_cruda

class DetectorSueldo:
    @staticmethod
    def extraer_de_texto(soup):
        texto_completo = soup.get_text(separator=" ")
        patron_estricto = r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s*US\$\s*/\s*(?:año|mes|yr|month|year))'
        matches = re.findall(patron_estricto, texto_completo, re.IGNORECASE)
        if matches:
            return " - ".join(matches[:2])
        return None

class ProcesadorData:
    @staticmethod
    def corregir_fecha(valor):
        if pd.isna(valor): return None
        try:
            if isinstance(valor, datetime):
                return valor.strftime("%Y-%m-%d %H:%M:%S")
            return str(valor)
        except (TypeError, ValueError):
            return str(valor)

def extraer_detalles_completos(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    }
    resultado = {"description": None, "salary_extracted": None}
    try:
        time.sleep(random.uniform(2, 5)) 
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            desc_tag = soup.find('div', {'class': 'show-more-less-html__markup'}) or \
                       soup.find('section', {'class': 'description'})
            if desc_tag:
                resultado["description"] = re.sub(r'[\r\n\t\s]+', ' ', desc_tag.get_text(separator=" ")).strip()
            resultado["salary_extracted"] = DetectorSueldo.extraer_de_texto(soup)
        return resultado
    except Exception:
        return resultado

def ejecutar_linkedin(roles, scrape_days: int = 2): 
    """
    Versión optimizada para ejecución diaria. 
    scrape_days se multiplica por 24 para obtener las horas exactas.
    """
    hours_old = scrape_days * 24 
    RESULTS_WANTED = 40 # LinkedIn suele limitar resultados públicos

    print("\n" + "="*60)
    print(f"🚀 SCRAPER LINKEDIN DIARIO ({hours_old} horas atrás)")
    print("="*60)

    df_lista = []
    for idx, t in enumerate(roles, 1): 
        print(f"[{idx}/{len(roles)}] 🔎 Buscando: {t.upper()}...")
        try:
            # JobSpy filtra por antigüedad usando hours_old
            jobs = scrape_jobs(
                site_name=["linkedin"],
                search_term=t,
                location="Ecuador",
                results_wanted=RESULTS_WANTED,
                hours_old=hours_old,
                linkedin_fetch_description=True 
            )
            if not jobs.empty:
                jobs['rol_busqueda'] = t
                jobs['plataforma'] = "linkedin"
                df_lista.append(jobs)
                print(f"   ✅ Encontradas: {len(jobs)} ofertas.")
        except Exception as e:
            print(f"   ❌ Error en JobSpy para '{t}': {e}")

    if not df_lista:
        print("\n⚠️ No se encontraron ofertas nuevas en LinkedIn.")
        return

    df = pd.concat(df_lista, ignore_index=True)
    df = df.drop_duplicates(subset=['job_url'])

    print(f"🕵️ Enriqueciendo {len(df)} ofertas...")
    
    exitos = 0
    for index, row in df.iterrows():
        url = row.get('job_url', '')
        desc_original = row.get('description', '')
        
        # Solo extraemos detalles si la descripción está incompleta
        if not desc_original or len(str(desc_original)) < 200:
            info = extraer_detalles_completos(url)
            descripcion = info["description"] if info["description"] else desc_original
            sueldo = info["salary_extracted"]
        else:
            descripcion = desc_original
            sueldo = None

        # Preparar data para jobs_raw
        datos = {
            'plataforma': 'linkedin',
            'rol_busqueda': row['rol_busqueda'],
            'fecha_publicacion': ProcesadorData.corregir_fecha(row.get('date_posted')),
            'oferta_laboral': row.get('title', 'Sin Título'),
            'locacion': row.get('location', 'Ecuador'),
            'descripcion': descripcion,
            'sueldo': sueldo,
            'compania': row.get('company', 'Confidencial'),
            'url_publicacion': url,
            'processed': False # Clave para que el limpiador las recoja
        }
        
        # Guardar con UPSERT (Evita duplicados en la DB)
        if guardar_oferta_cruda(datos):
            exitos += 1
        
        if (index + 1) % 5 == 0:
            print(f"   ↳ Procesadas {index+1}/{len(df)}...")

    print(f"✨ LINKEDIN FINALIZADO: {exitos} registros nuevos/actualizados.")

if __name__ == "__main__":
    ejecutar_linkedin(["desarrollador python"], scrape_days=2)