import sys
import os
import time
from datetime import datetime

# Importar roles seleccionados
ROLES_GLOBALES = [
    "desarrollador python"
]

def main():
    # Parámetro dinámico: python main.py [dias]
    # Por defecto 2 días para el cron job diario en Contabo
    scrape_days = int(sys.argv[1]) if len(sys.argv) > 1 else 2

    start_time = time.time()
    print("\n" + "█" * 60)
    print(f"🚀 DEVRADAR ECUADOR - PIPELINE AUTOMATIZADO")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔎 Rango: Últimos {scrape_days} días")
    print("█" * 60 + "\n")

    # =========================================================
    # FASE 1: RECOLECCIÓN (SCRAPING)
    # =========================================================
    print("📡 --- FASE 1: RECOLECCIÓN DE OFERTAS ---")

    # 1. COMPUTRABAJO
    try:
        from scrapers.scraper_computrabajos import correr_scraper_computrabajo
        print("\n🔹 [1/3] EJECUTANDO COMPUTRABAJO...")
        correr_scraper_computrabajo(ROLES_GLOBALES, dias=scrape_days)
    except Exception as e:
        print(f"❌ Error en Computrabajo: {e}")

    # 2. JOOBLE
    try:
        from scrapers.scraper_jooble import correr_scraper_jooble
        print("\n🔹 [2/3] EJECUTANDO JOOBLE...")
        correr_scraper_jooble(ROLES_GLOBALES, dias=scrape_days)
    except Exception as e:
        print(f"❌ Error en Jooble: {e}")

    # 3. LINKEDIN
    try:
        from scrapers.scraper_linkedin import ejecutar_linkedin
        print("\n🔹 [3/3] EJECUTANDO LINKEDIN...")
        ejecutar_linkedin(ROLES_GLOBALES, scrape_days=scrape_days)
    except Exception as e:
        print(f"❌ Error en LinkedIn: {e}")

    # =========================================================
    # FASE 2: LIMPIEZA E INTELIGENCIA ARTIFICIAL
    # =========================================================
    print("\n" + "=" * 60)
    print("🧠 --- FASE 2: PROCESAMIENTO CON IA (GROQ) ---")
    print("=" * 60)
    
    try:
        # Importamos y ejecutamos el limpiador
        from limpiador.limpiador_de_datos import ejecutar_limpieza_ia
        print("\n🔹 Procesando nuevas ofertas detectadas...")
        ejecutar_limpieza_ia() # Solo limpia donde processed=False
    except Exception as e:
        print(f"❌ Error fatal en el Limpiador IA: {e}")

    duration = time.time() - start_time
    print("\n" + "█" * 60)
    print(f"✅ PIPELINE FINALIZADO EN {int(duration // 60)}m {int(duration % 60)}s")
    print("█" * 60)

if __name__ == "__main__":
    main()