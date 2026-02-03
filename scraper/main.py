import sys
import os
import time
from datetime import datetime

# =============================================================================
# 🛠️ CONFIGURACIÓN DE ROLES (LA LISTA MAESTRA)
# =============================================================================
ROLES_GLOBALES = [
    # --- DESARROLLO & PROGRAMACIÓN ---
    "cybersecurity",
]

# =============================================================================
# 🏁 FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    start_time = time.time()
    print("\n" + "█" * 60)
    print(f"🚀 INICIANDO DEVRADAR - PIPELINE COMPLETO")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔎 Roles a buscar: {len(ROLES_GLOBALES)}")
    print("█" * 60 + "\n")

    # =========================================================
    # FASE 1: RECOLECCIÓN (SCRAPING)
    # =========================================================
    print("📡 --- FASE 1: RECOLECCIÓN DE OFERTAS ---")

    # 1. COMPUTRABAJO
    try:
        from scrapers.scraper_computrabajos import RecolectorComputrabajo
        print("\n🔹 [1/3] EJECUTANDO COMPUTRABAJO...")
        bot_ct = RecolectorComputrabajo(ROLES_GLOBALES, scrape_days=60)
        bot_ct.recolectar()
    except Exception as e:
        print(f"❌ Error fatal en Computrabajo: {e}")

    # 2. JOOBLE
    try:
        from scrapers.scraper_jooble import RecolectorJooble
        print("\n🔹 [2/3] EJECUTANDO JOOBLE...")
        bot_jb = RecolectorJooble(ROLES_GLOBALES, scrape_days=60)
        bot_jb.recolectar()
    except Exception as e:
        print(f"❌ Error fatal en Jooble: {e}")

    # 3. LINKEDIN
    try:
        from scrapers.scraper_linkedin import ejecutar as ejecutar_linkedin
        print("\n🔹 [3/3] EJECUTANDO LINKEDIN...")
        ejecutar_linkedin(ROLES_GLOBALES, scrape_days=30)
    except Exception as e:
        print(f"❌ Error fatal en LinkedIn: {e}")

    # =========================================================
    # FASE 2: LIMPIEZA E INTELIGENCIA ARTIFICIAL
    # =========================================================
    print("\n" + "=" * 60)
    print("🧠 --- FASE 2: PROCESAMIENTO CON IA (GROQ) ---")
    print("=" * 60)
    
    try:
        # CORREGIDO: Ahora apunta a 'limpiador_de_datos.py' que es el nombre real
        from limpiador.limpiador_de_datos import ejecutar_limpieza_ia
        
        print("\n🔹 Iniciando limpieza, estandarización y embeddings...")
        ejecutar_limpieza_ia()
        
    except ImportError as e:
        print(f"⚠️ Error de importación: {e}")
        print("Revisa que el archivo 'limpiador/limpiador_de_datos.py' exista.")
    except Exception as e:
        print(f"❌ Error fatal en el Limpiador IA: {e}")

    # =========================================================
    # FIN DEL PROCESO
    # =========================================================
    duration = time.time() - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    
    print("\n" + "█" * 60)
    print(f"✅ PIPELINE FINALIZADO CORRECTAMENTE")
    print(f"⏱️ Tiempo total: {minutes}m {seconds}s")
    print("💤 Durmiendo hasta la próxima ejecución...")
    print("█" * 60)

if __name__ == "__main__":
    main()