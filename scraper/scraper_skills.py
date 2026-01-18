import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException
import json
import time
import random
import re
import os
import urllib3

# --- CONFIGURACIÓN ---
ARCHIVO_ENTRADA = "base_datos_filtrada.json"  # <-- El archivo limpio
ARCHIVO_SALIDA = "dataset_final_definitivo.json"

TECH_STACK = [
    "Python", "Java", "JavaScript", "TypeScript", "C#", ".NET", "PHP", "Go", "Golang",
    "React", "Angular", "Vue", "Node", "Spring", "Django", "Flask", "Laravel",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "Redis",
    "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Git", "Linux",
    "Excel", "Power BI", "Tableau", "Machine Learning", "AI", "Scrum", "Agile",
    "English", "Inglés"
]

def iniciar_driver():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.page_load_strategy = 'eager' # Carga rápida
    try:
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(20) # 20 segs máximo de espera
        return driver
    except:
        time.sleep(5)
        return uc.Chrome(options=options)

def limpiar_obstaculos(driver):
    try:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0.5)
        botones = driver.find_elements(By.XPATH, "//div[contains(text(), 'Mostrar más')] | //a[contains(text(), 'Mostrar más')]")
        for btn in botones:
            driver.execute_script("arguments[0].click();", btn)
    except: pass

def scraper_inmortal():
    print("🤖 Iniciando Scraper INMORTAL...")
    
    try:
        with open(ARCHIVO_ENTRADA, "r", encoding="utf-8") as f:
            maestra = json.load(f)
        print(f"📂 Cargadas {len(maestra)} ofertas para procesar.")
    except:
        print(f"❌ No existe '{ARCHIVO_ENTRADA}'. Corre primero 'limpiador_de_datos.py'.")
        return

    # Recuperar progreso
    procesados = set()
    progreso = []
    if os.path.exists(ARCHIVO_SALIDA):
        try:
            with open(ARCHIVO_SALIDA, "r", encoding="utf-8") as f:
                progreso = json.load(f)
                for job in progreso:
                    if job.get("revisado"): procesados.add(job["link"])
            print(f"♻️ Recuperadas {len(procesados)} ofertas ya listas.")
        except:
            progreso = maestra
    else:
        progreso = maestra

    print("\n⏳ Abriendo navegador...")
    driver = iniciar_driver()
    input("\n🛑 Pasa el Cloudflare y presiona ENTER...")

    try:
        for i, oferta in enumerate(progreso):
            url = oferta.get("link")
            
            if not url or url in procesados: continue

            print(f"\n({i+1}/{len(progreso)}) {oferta.get('titulo', '')[:40]}...")

            # --- INTENTO DE NAVEGACIÓN BLINDADO ---
            try:
                driver.get(url)
            except (TimeoutException, WebDriverException, urllib3.exceptions.ReadTimeoutError):
                print("   🔥 ¡Timeout detectado! Reiniciando navegador...")
                try: driver.quit()
                except: pass
                driver = iniciar_driver()
                continue # Saltamos esta oferta problemática y seguimos a la siguiente

            time.sleep(random.uniform(2, 3))
            limpiar_obstaculos(driver)

            try:
                cuerpo = driver.find_element(By.TAG_NAME, "body").text
                cuerpo_lower = cuerpo.lower()

                # Skills
                skills = []
                for tech in TECH_STACK:
                    patrones = [f" {tech.lower()} ", f"/{tech.lower()}", f"\n{tech.lower()}", f"({tech.lower()})", f", {tech.lower()}"]
                    if any(p in cuerpo_lower for p in patrones):
                        if tech not in skills: skills.append(tech)
                
                oferta["skills_detectadas"] = skills
                
                # Salario
                salario = oferta.get("salario_detectado")
                if not salario or salario == "No especificado":
                    patron = r'(\$\s?[\d,.]+|[\d,.]+\s?usd|[\d,.]+\s?dolares|usd\s?[\d,.]+)'
                    posibles = re.findall(patron, cuerpo, re.IGNORECASE)
                    if posibles:
                        oferta["salario_detectado"] = posibles[0]
                        print(f"   💰 Salario: {posibles[0]}")

                oferta["revisado"] = True
                procesados.add(url)
                
                if skills: print(f"   ✅ Skills: {skills}")
                else: print("   🤔 Sin skills obvias.")

                # Guardado en cada paso
                with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
                    json.dump(progreso, f, indent=4, ensure_ascii=False)

            except Exception as e:
                print(f"   ❌ Error leyendo: {e}")

    finally:
        try: driver.quit()
        except: pass
        print(f"\n💾 FIN. Todo guardado en '{ARCHIVO_SALIDA}'")

if __name__ == "__main__":
    scraper_inmortal()