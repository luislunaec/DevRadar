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
            # Filtro para evitar números bajos que no son sueldos
            sueldos_validos = [m for m in matches_sec if float(m.split()[0].replace('.', '').replace(',', '.')) > 100]
            if sueldos_validos:
                return " - ".join(sueldos_validos[:2])
        return None


class ProcesadorData:
    @staticmethod
    def corregir_fecha(valor):
        if pd.isna(valor): return None
        try:
            # JobSpy a veces devuelve fechas como objetos datetime o strings
            if isinstance(valor, str):
                return valor # Si ya es texto, lo dejamos (JobSpy suele dar YYYY-MM-DD)
            if isinstance(valor, (int, float)) or str(valor).isdigit():
                # Timestamp unix
                unit = 'ms' if len(str(int(valor))) > 10 else 's'
                return pd.to_datetime(int(valor), unit=unit).strftime('%Y-%m-%d')
            if isinstance(valor, datetime):
                 return valor.strftime('%Y-%m-%d')
            return str(valor)
        except:
            return str(valor)


def extraer_detalles_completos(url):
    """
    Intenta entrar a la URL directa para sacar descripción full y sueldos ocultos.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9",
    }
    resultado = {"description": None, "salary_extracted": None}

    try:
        # Pausa aleatoria para evitar bloqueo de IP (LinkedIn es celoso)
        time.sleep(random.uniform(2, 5)) 
        
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')

            # Selectores comunes de descripción en LinkedIn público
            desc_tag = soup.find('div', {'class': 'show-more-less-html__markup'}) or \
                       soup.find('section', {'class': 'description'}) or \
                       soup.find('div', {'class': 'description__text'})
            
            if desc_tag:
                texto = desc_tag.get_text(separator=" ")
                resultado["description"] = re.sub(r'[\r\n\t\s]+', ' ', texto).strip()

            resultado["salary_extracted"] = DetectorSueldo.extraer_de_texto(soup)

        return resultado
    except Exception as e:
        # print(f"   ⚠️ No se pudo extraer detalle extra: {e}") 
        return resultado


def ejecutar(roles, scrape_days: int = 30): 
    
    # 💥 ESTRATEGIA MAX RECORDS:
    # Si piden más de 7 días, buscamos 720 horas (30 días).
    hours_old = 720 if scrape_days > 7 else scrape_days * 24
    
    # Cantidad de resultados deseados por rol (Aumentado de 5 a 50)
    # Nota: LinkedIn público suele capar a ~25-100 resultados. Poner mucho más puede dar error.
    RESULTS_WANTED = 50 

    print("\n" + "="*60)
    print("🚀 INICIANDO SCRAPER LINKEDIN (MODO TURBO)")
    print(f"   📅 Historial: {hours_old} horas atrás")
    print(f"   🎯 Meta: {RESULTS_WANTED} ofertas por rol")
    print("="*60)

    df_lista = []

    for idx, t in enumerate(roles, 1): 
        print(f"\n[{idx}/{len(roles)}] 🔎 Buscando: {t.upper()}...")
        try:
            # JobSpy hace el trabajo sucio
            jobs = scrape_jobs(
                site_name=["linkedin"],
                search_term=t,
                location="Ecuador",
                results_wanted=RESULTS_WANTED,
                hours_old=hours_old,
                country_indeed='Ecuador', # A veces ayuda a configurar el entorno
                linkedin_fetch_description=True # Intentar que JobSpy traiga la descripción de una
            )
            
            print(f"   ✅ JobSpy encontró: {len(jobs)} ofertas.")

            if not jobs.empty:
                jobs['rol_busqueda'] = t
                jobs['plataforma'] = "linkedin"
                df_lista.append(jobs)
            else:
                print("   ⚠️ No se encontraron resultados para este rol.")

        except Exception as e:
            print(f"   ❌ Error en JobSpy para '{t}': {e}")
            continue # Si falla uno, seguimos con el siguiente

    # --- PROCESAMIENTO FINAL ---
    if not df_lista:
        print("\n⚠️ ALERTA: No se recolectó NADA de LinkedIn. Posible bloqueo o fallo de librería.")
        return

    print("\n🔄 Unificando y procesando datos...")
    # Unir todos los dataframes
    df = pd.concat(df_lista, ignore_index=True)
    
    # Eliminar duplicados por URL
    if 'job_url' in df.columns:
        df = df.drop_duplicates(subset=['job_url'])
    else:
        print("⚠️ Columna job_url no encontrada, saltando deduplicación.")

    # Corregir fechas
    if 'date_posted' in df.columns:
        df['date_posted'] = df['date_posted'].apply(ProcesadorData.corregir_fecha)

    # Listas para enriquecer data
    descripciones_finales = []
    sueldos_finales = []

    print(f"🕵️ Extrayendo detalles profundos de {len(df)} ofertas (Esto toma tiempo)...")
    
    for index, row in df.iterrows():
        url = row.get('job_url', '')
        desc_original = row.get('description', '')
        
        # Si JobSpy ya trajo una descripción decente (>100 chars), la usamos para no hacer peticiones extra
        # Si es muy corta o nula, intentamos entrar al link (Scraping manual)
        if desc_original and len(str(desc_original)) > 100:
            descripciones_finales.append(desc_original)
            # Intentar sacar sueldo del texto que ya tenemos
            # (Aquí podrías llamar a DetectorSueldo con BeautifulSoup(desc_original) si quisieras pulir más)
            sueldos_finales.append(None) 
        else:
            # Si no hay descripción buena, entramos a la web (Lento pero seguro)
            info = extraer_detalles_completos(url)
            
            # Prioridad: Lo que sacamos manual > Lo que trajo JobSpy
            desc_final = info["description"] if info["description"] != "No disponible" else desc_original
            descripciones_finales.append(desc_final)
            sueldos_finales.append(info["salary_extracted"])
            
            # Feedback visual cada 5 ofertas
            if index % 5 == 0:
                print(f"   ↳ Procesando oferta {index+1}...")

    # Construcción del DataFrame Final para Supabase
    df_final = pd.DataFrame({
        "plataforma": df['plataforma'],
        "rol_busqueda": df['rol_busqueda'],
        "fecha_publicacion": df.get('date_posted', ''), # .get por si la columna falta
        "oferta_laboral": df.get('title', 'Sin Título'),
        "locacion": df.get('location', 'Ecuador'),
        "descripcion": descripciones_finales,
        "sueldo": sueldos_finales,
        "compania": df.get('company', 'Confidencial'),
        "url_publicacion": df.get('job_url', '')
    })

    # Guardar en Supabase
    print(f"\n💾 Guardando {len(df_final)} registros en Supabase...")
    exitos = 0
    errores = 0
    for _, row in df_final.iterrows():
        datos = {
            'plataforma': row['plataforma'],
            'rol_busqueda': row['rol_busqueda'],
            'fecha_publicacion': row['fecha_publicacion'],
            'oferta_laboral': row['oferta_laboral'],
            'locacion': row['locacion'],
            'descripcion': row['descripcion'],
            'sueldo': row['sueldo'],
            'compania': row['compania'],
            'url_publicacion': row['url_publicacion']
        }
        
        # Validación extra de campos nulos
        if pd.isna(datos['fecha_publicacion']): datos['fecha_publicacion'] = None
        if pd.isna(datos['sueldo']): datos['sueldo'] = None

        if guardar_oferta_cruda(datos):
            exitos += 1
        else:
            errores += 1
        time.sleep(0.01) # Respiro para la API
    
    print(f"✨ LINKEDIN FINALIZADO: {exitos} guardados exitosamente ({errores} fallidos).")


if __name__ == "__main__":
    # Prueba manual si ejecutas este archivo solo
    ROLES_TEST = ["desarrollador python", "analista de datos"]
    ejecutar(ROLES_TEST, scrape_days=30)