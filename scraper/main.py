"""
Clase principal para ejecutar el flujo completo de scraping.
Solo se obtienen ofertas recientes según SCRAPE_DAYS; scrapers hacen append en jobs_raw.
"""
import os
import time
from dotenv import load_dotenv
from scrapers.scraper_computrabajos import RecolectorComputrabajo, ROLES_DEFAULT
from scrapers.scraper_linkedin import ejecutar as ejecutar_linkedin
from scrapers.scraper_jooble import recolector_fuerza_bruta
from limpiador.limpiador_de_datos import ejecutar_limpieza_ia

load_dotenv()
# Cuántos días hacia atrás obtener ofertas (configurable por código o .env)
SCRAPE_DAYS = int(os.getenv("SCRAPE_DAYS", "7"))


class ScraperMain:
    """Clase principal que orquesta el flujo completo de scraping"""

    def __init__(self, scrape_days: int | None = None):
        self.scrape_days = scrape_days if scrape_days is not None else SCRAPE_DAYS
        self.inicio_total = time.time()
        print("=" * 70)
        print("🚀 INICIANDO FLUJO COMPLETO DE SCRAPING")
        print("=" * 70)
        print(f"📅 SCRAPE_DAYS = {self.scrape_days} (solo ofertas de los últimos {self.scrape_days} días)")
        print("=" * 70)

    def ejecutar_scrapers(self):
        """Ejecuta los 3 scrapers en secuencia (solo ofertas recientes; append en jobs_raw)"""
        print("\n" + "=" * 70)
        print("📡 FASE 1: EJECUTANDO SCRAPERS")
        print("=" * 70)

        # 1. Scraper Computrabajo
        print("\n[1/3] 🟦 Ejecutando scraper de Computrabajo...")
        try:
            bot = RecolectorComputrabajo(ROLES_DEFAULT, scrape_days=self.scrape_days)
            bot.recolectar(paginas_por_rol=3)
            print("✅ Computrabajo completado")
        except Exception as e:
            print(f"❌ Error en Computrabajo: {e}")

        time.sleep(2)  # Pausa entre scrapers

        # 2. Scraper LinkedIn
        print("\n[2/3] 🔵 Ejecutando scraper de LinkedIn...")
        try:
            ejecutar_linkedin(scrape_days=self.scrape_days)
            print("✅ LinkedIn completado")
        except Exception as e:
            print(f"❌ Error en LinkedIn: {e}")

        time.sleep(2)  # Pausa entre scrapers

        # 3. Scraper Jooble
        print("\n[3/3] 🟢 Ejecutando scraper de Jooble...")
        try:
            recolector_fuerza_bruta(scrape_days=self.scrape_days)
            print("✅ Jooble completado")
        except Exception as e:
            print(f"❌ Error en Jooble: {e}")
        
        print("\n" + "=" * 70)
        print("✅ FASE 1 COMPLETADA: Todos los scrapers ejecutados")
        print("=" * 70)
    
    def ejecutar_limpiador(self):
        """Ejecuta el limpiador de datos que añade habilidades"""
        print("\n" + "=" * 70)
        print("🧹 FASE 2: LIMPIEZA DE DATOS Y EXTRACCIÓN DE HABILIDADES")
        print("=" * 70)
        
        try:
            ejecutar_limpieza_ia()
            print("\n" + "=" * 70)
            print("✅ FASE 2 COMPLETADA: Datos limpiados con habilidades guardados en jobs_clean")
            print("=" * 70)
        except Exception as e:
            print(f"❌ Error en limpiador: {e}")
    
    def ejecutar_flujo_completo(self):
        """Ejecuta el flujo completo"""
        try:
            # Fase 1: Scrapers
            self.ejecutar_scrapers()
            
            # Fase 2: Limpiador (añade habilidades)
            self.ejecutar_limpiador()
            
            # Resumen final
            tiempo_total = time.time() - self.inicio_total
            print("\n" + "=" * 70)
            print("🎉 FLUJO COMPLETO FINALIZADO")
            print("=" * 70)
            print(f"⏱️  Tiempo total: {tiempo_total:.2f} segundos ({tiempo_total/60:.2f} minutos)")
            print("=" * 70)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Proceso interrumpido por el usuario")
        except Exception as e:
            print(f"\n\n❌ Error crítico: {e}")


if __name__ == "__main__":
    main = ScraperMain()  # usa SCRAPE_DAYS por defecto; o: ScraperMain(scrape_days=3)
    main.ejecutar_flujo_completo()
