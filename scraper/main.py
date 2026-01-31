"""
Clase principal para ejecutar el flujo completo de scraping
"""
import time
from scraper_computrabajos import RecolectorComputrabajo
from scraper_linkedin import ejecutar as ejecutar_linkedin
from scraper_jooble import recolector_fuerza_bruta
from limpiador_de_datos import ejecutar_limpieza_base


class ScraperMain:
    """Clase principal que orquesta el flujo completo de scraping"""
    
    def __init__(self):
        self.inicio_total = time.time()
        print("=" * 70)
        print("🚀 INICIANDO FLUJO COMPLETO DE SCRAPING")
        print("=" * 70)
    
    def ejecutar_scrapers(self):
        """Ejecuta los 3 scrapers en secuencia"""
        print("\n" + "=" * 70)
        print("📡 FASE 1: EJECUTANDO SCRAPERS")
        print("=" * 70)
        
        # 1. Scraper Computrabajo
        print("\n[1/3] 🟦 Ejecutando scraper de Computrabajo...")
        try:
            # Usar los roles definidos en scraper_computrabajos.py
            from scraper_computrabajos import ROLES_DEFAULT
            bot = RecolectorComputrabajo(ROLES_DEFAULT)
            bot.recolectar(paginas_por_rol=3)
            print("✅ Computrabajo completado")
        except Exception as e:
            print(f"❌ Error en Computrabajo: {e}")
        
        time.sleep(2)  # Pausa entre scrapers
        
        # 2. Scraper LinkedIn
        print("\n[2/3] 🔵 Ejecutando scraper de LinkedIn...")
        try:
            ejecutar_linkedin()
            print("✅ LinkedIn completado")
        except Exception as e:
            print(f"❌ Error en LinkedIn: {e}")
        
        time.sleep(2)  # Pausa entre scrapers
        
        # 3. Scraper Jooble
        print("\n[3/3] 🟢 Ejecutando scraper de Jooble...")
        try:
            recolector_fuerza_bruta()
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
            ejecutar_limpieza_base()
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
    main = ScraperMain()
    main.ejecutar_flujo_completo()
