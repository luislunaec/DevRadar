import os
import sys
import pandas as pd
from jobspy import scrape_jobs
import requests
from bs4 import BeautifulSoup
import time
import random
import re

# Permitir imports cuando se ejecuta directamente desde scrapers/
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
            if len(matches) >= 2:
                return f"{matches[0]} - {matches[1]}"
            return matches[0]

        patron_secundario = r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?\s*US\$)'
        matches_sec = re.findall(patron_secundario, texto_completo)

        if matches_sec:
            sueldos_validos = [m for m in matches_sec if float(m.split()[0].replace('.', '').replace(',', '.')) > 100]
            if sueldos_validos:
                return " - ".join(sueldos_validos[:2])
        return None


class ProcesadorData:
    @staticmethod
    def corregir_fecha(valor):
        if pd.isna(valor): return None
        try:
            if isinstance(valor, (int, float)) or str(valor).isdigit():
                unit = 'ms' if len(str(int(valor))) > 10 else 's'
                return pd.to_datetime(int(valor), unit=unit).strftime('%Y-%m-%d')
            return str(valor)
        except:
            return str(valor)


def extraer_detalles_completos(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
    }
    resultado = {"description": "No disponible", "salary_extracted": None}

    try:
        time.sleep(random.uniform(2, 4))
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')

            desc_tag = soup.find('div', {'class': 'show-more-less-html__markup'}) or \
                       soup.find('section', {'class': 'description'})
            if desc_tag:
                # SE MANTIENE LA Ñ Y TILDES (No se usa encoding ascii)
                texto = desc_tag.get_text(separator=" ")
                resultado["description"] = re.sub(r'[\r\n\t\s]+', ' ', texto).strip()

            resultado["salary_extracted"] = DetectorSueldo.extraer_de_texto(soup)

        return resultado
    except Exception as e:
        print(f"Error en URL {url}: {e}")
        return resultado


def ejecutar():
    print("🚀 INICIANDO SCRAPER...")

    busquedas = ["Desarrollador Software", "Fullstack Developer", "Backend Developer", "Frontend Developer",
                 "Product Owner"]
    df_lista = []

    for t in busquedas:
        print(f"Buscando: {t}...")
        # Aquí forzamos linkedin como plataforma
        jobs = scrape_jobs(site_name=["linkedin"], search_term=t, location="Ecuador", results_wanted=5)
        jobs['rol_busqueda'] = t
        jobs['plataforma'] = "linkedin"
        df_lista.append(jobs)

    df = pd.concat(df_lista).drop_duplicates(subset=['job_url'])
    df['date_posted'] = df['date_posted'].apply(ProcesadorData.corregir_fecha)

    descripciones = []
    sueldos = []

    for url in df['job_url']:
        info = extraer_detalles_completos(url)
        descripciones.append(info["description"])
        sueldos.append(info["salary_extracted"])
        print(f"🔗 Procesado: {url[:40]}... | Sueldo: {info['salary_extracted']}")

    # Formato final solicitado
    df_final = pd.DataFrame({
        "plataforma": df['plataforma'],
        "rol_busqueda": df['rol_busqueda'],
        "fecha_publicacion": df['date_posted'],
        "oferta_laboral": df['title'],
        "locacion": df['location'],
        "descripcion": descripciones,
        "sueldo": sueldos,
        "compania": df['company'],
        "url_publicacion": df['job_url']
    })

    # Guardar directamente en Supabase
    exitos = 0
    errores = 0
    for _, row in df_final.iterrows():
        datos = {
            'plataforma': row.get('plataforma', 'linkedin'),
            'rol_busqueda': row.get('rol_busqueda', ''),
            'fecha_publicacion': row.get('fecha_publicacion', ''),
            'oferta_laboral': row.get('oferta_laboral', 'Sin Título'),
            'locacion': row.get('locacion', 'Ecuador'),
            'descripcion': row.get('descripcion', ''),
            'sueldo': row.get('sueldo'),
            'compania': row.get('compania', 'Confidencial'),
            'url_publicacion': row.get('url_publicacion', '')
        }
        
        if guardar_oferta_cruda(datos):
            exitos += 1
        else:
            errores += 1
        time.sleep(0.05)
    
    print(f"✨ Proceso finalizado. {exitos}/{len(df_final)} ofertas guardadas en Supabase (jobs_raw)")
    if errores > 0:
        print(f"⚠️ {errores} ofertas no se pudieron guardar")


if __name__ == "__main__":
    ejecutar()
