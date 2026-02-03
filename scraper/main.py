import os
import time
from dotenv import load_dotenv

# Importamos las Clases/Funciones
from scrapers.scraper_computrabajos import RecolectorComputrabajo
from scrapers.scraper_linkedin import ejecutar as ejecutar_linkedin
from scrapers.scraper_jooble import RecolectorJooble 
from limpiador.limpiador_de_datos import ejecutar_limpieza_ia

load_dotenv()
# Por defecto 30 días si no hay nada en el .env
SCRAPE_DAYS = int(os.getenv("SCRAPE_DAYS", "30"))

# =============================================================================
# 📜 LA LISTA MAESTRA (AQUÍ MANDAS TÚ)
# =============================================================================
ROLES_GLOBALES = [
    # --- DESARROLLO ---
    "programador", "desarrollador software", "desarrollador fullstack", 
    "desarrollador backend", "desarrollador frontend", "desarrollador movil",
    "ingeniero de sistemas", "sistemas de informacion",
    
    # --- LENGUAJES ---
    "python developer", "java developer", "javascript developer", 
    ".net developer", "php developer", "c# developer", 
    
    # --- DATA & INFRA ---
    "data analyst", "data engineer", "sql developer", "business intelligence",
    "devops engineer", "cloud engineer", "aws engineer", "administrador linux",
    
    # --- QA & SEGURIDAD ---
    "qa automation", "qa engineer", "tester de software",
    "ciberseguridad", "seguridad informatica"
]

class ScraperMain:
    def __init__(self, scrape_days: int | None = None):
        # Si le pasas días los usa, si no, usa el global (30)
        self.scrape_days = scrape_days if scrape_days is not None else SCRAPE_DAYS
        self.roles = ROLES_GLOBALES # <--- Aquí guardamos la lista maestra
        
        self.inicio_total = time.time()
        print("=" * 70)
        print(f"🚀 INICIANDO SCRAPING (Días: {self.scrape_days})")
        print(f"📋 Buscando {len(self.roles)} perfiles en todas las plataformas")
        print("=" * 70)

    def ejecutar_scrapers(self):
        print("\n📡 FASE 1: EJECUTANDO SCRAPERS")

        # 1. COMPUTRABAJO
        print("\n[1/3] 🟦 Computrabajo...")
        try:
            # LE PASAMOS LA LISTA MAESTRA (self.roles)
            bot = RecolectorComputrabajo(self.roles, scrape_days=self.scrape_days)
            bot.recolectar(paginas_por_rol=3)
        except Exception as e:
            print(f"❌ Error Computrabajo: {e}")

        time.sleep(2)

        # 2. JOOBLE
        print("\n[2/3] 🟢 Jooble...")
        try:
            # LE PASAMOS LA LISTA MAESTRA (self.roles)
            bot_jooble = RecolectorJooble(self.roles, scrape_days=self.scrape_days)
            bot_jooble.recolectar()
        except Exception as e:
            print(f"❌ Error Jooble: {e}")

        time.sleep(2)

        # 3. LINKEDIN
        print("\n[3/3] 🔵 LinkedIn...")
        try:
            # LE PASAMOS LA LISTA MAESTRA (self.roles)
            ejecutar_linkedin(self.roles, scrape_days=self.scrape_days)
        except Exception as e:
            print(f"❌ Error LinkedIn: {e}")

    def ejecutar_flujo_completo(self):
        try:
            self.ejecutar_scrapers()
            print("\n🧹 FASE 2: LIMPIEZA IA...")
            try: ejecutar_limpieza_ia()
            except: pass
            
            total = (time.time() - self.inicio_total) / 60
            print(f"\n🎉 TODO TERMINADO EN {total:.2f} MINUTOS")
        except KeyboardInterrupt:
            print("\n🛑 Cancelado por usuario")

if __name__ == "__main__":
    # Aquí puedes forzar los días que quieras
    app = ScraperMain(scrape_days=30)
    app.ejecutar_flujo_completo()