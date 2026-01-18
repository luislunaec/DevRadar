import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json
import time
import random

def recolector_scroll_infinito():
    print("📜 Iniciando RECOLECCIÓN POR SCROLL INFINITO...")
    print("🎯 Meta: Bajar y bajar hasta tener muchas ofertas.")
    
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    
    # Usamos un conjunto (set) para evitar guardar la misma oferta dos veces
    links_vistos = set()
    lista_final_ofertas = []
    
    try:
        # 1. Entrar a la página PRINCIPAL (Sin números de página)
        url = "https://ec.jooble.org/SearchResult?ukw=programador&rgns=Quito"
        driver.get(url)
        
        print("⏳ Esperando 10 segundos para que cargue la primera tanda...")
        time.sleep(10)
        
        # --- BUCLE DE SCROLL ---
        # Haremos esto hasta tener 1000 ofertas o hasta que no haya más
        intentos_sin_nuevos = 0
        
        while len(lista_final_ofertas) < 1000:
            # 1. Guardamos la altura actual de la página
            altura_antes = driver.execute_script("return document.body.scrollHeight")
            
            # 2. BAJAMOS HASTA EL FONDO (Scroll)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # También presionamos la tecla END por si acaso el JS no activa la carga
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            except: pass
            
            print(f"⬇️ Bajando... (Esperando carga de nuevas ofertas)")
            time.sleep(random.uniform(4, 6)) # Esperamos a que aparezcan las nuevas
            
            # 3. EXTRAEMOS LO QUE VEMOS EN PANTALLA
            # Usamos el selector CORREGIDO que tú me diste: _jobCard
            tarjetas = driver.find_elements(By.CSS_SELECTOR, "div[data-test-name='_jobCard']")
            
            nuevos_en_esta_bajada = 0
            
            for tarjeta in tarjetas:
                try:
                    # Sacamos el Link (es lo más importante para filtrar repetidos)
                    try:
                        elemento_link = tarjeta.find_element(By.TAG_NAME, "a")
                        link = elemento_link.get_attribute("href")
                    except: 
                        continue # Si no tiene link, no nos sirve

                    # Si es un link nuevo, guardamos todo
                    if link and link not in links_vistos:
                        links_vistos.add(link)
                        
                        # Sacamos Título
                        try:
                            titulo = tarjeta.find_element(By.TAG_NAME, "h2").text
                        except: titulo = "Sin Título"
                        
                        # Sacamos Salario (Buscamos texto con $)
                        salario = "No especificado"
                        try:
                            texto_tarjeta = tarjeta.text
                            for linea in texto_tarjeta.split('\n'):
                                if "$" in linea or "mensual" in linea.lower():
                                    salario = linea
                                    break
                        except: pass

                        # Agregamos a la lista oficial
                        lista_final_ofertas.append({
                            "id": len(lista_final_ofertas) + 1,
                            "titulo": titulo,
                            "salario_detectado": salario,
                            "link": link
                        })
                        nuevos_en_esta_bajada += 1
                except:
                    pass

            print(f"   ✨ Encontré {nuevos_en_esta_bajada} ofertas NUEVAS en esta bajada.")
            print(f"   📦 TOTAL ACUMULADO: {len(lista_final_ofertas)} ofertas.")
            
            # 4. VERIFICACIÓN DE FIN
            if nuevos_en_esta_bajada == 0:
                intentos_sin_nuevos += 1
                print(f"   ⚠️ No salieron nuevas... Intentando bajar más fuerte ({intentos_sin_nuevos}/5)")
                
                # A veces sale un botón de "Mostrar más", intentamos clickearlo
                try:
                    botones = driver.find_elements(By.TAG_NAME, "button")
                    for btn in botones:
                        if "más" in btn.text.lower() or "more" in btn.text.lower():
                            btn.click()
                            print("   👆 Click en botón 'Mostrar más'")
                            time.sleep(3)
                            break
                except: pass
                
                if intentos_sin_nuevos >= 5:
                    print("🛑 Parece que llegamos al final de la lista. No hay más trabajos.")
                    break
            else:
                intentos_sin_nuevos = 0 # Reiniciamos contador porque sí encontramos

            # 5. GUARDADO DE SEGURIDAD (Cada vez que encontramos algo)
            with open("base_datos_masiva.json", "w", encoding="utf-8") as f:
                json.dump(lista_final_ofertas, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        print("🏁 Cerrando navegador.")
        print(f"💾 Archivo final guardado: 'base_datos_masiva.json' con {len(lista_final_ofertas)} datos.")
        driver.quit()

if __name__ == "__main__":
    recolector_scroll_infinito()