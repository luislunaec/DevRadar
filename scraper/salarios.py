import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Cargar variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: No se encontró GEMINI_API_KEY en el archivo .env")

genai.configure(api_key=API_KEY)

# Nombre del modelo inicial
MODEL_NAME = 'models/gemini-flash-latest'

# Inicializamos el modelo globalmente
try:
    model = genai.GenerativeModel(MODEL_NAME)
except:
    model = genai.GenerativeModel('models/gemini-pro')

def extraer_salario_con_ia(texto_oferta):
    # --- CORRECCIÓN: Declaramos que vamos a usar la variable global AQUÍ ---
    global model 
    
    # Si el texto es muy corto, no gastamos saldo
    if not texto_oferta or len(str(texto_oferta)) < 10: 
        return "No especificado"

    prompt = f"""
    Analiza esta oferta de trabajo de Ecuador y extrae el SALARIO MENSUAL.
    TEXTO: '''{texto_oferta[:2000]}'''
    
    REGLAS:
    1. Si es por hora, multiplica por 160.
    2. Si es diario, multiplica por 22.
    3. Si es semanal, multiplica por 4.
    4. "Sueldo Básico" = 460.
    5. Si es rango, saca el promedio.
    
    Responde SOLO el número entero (ej: 800) o "No especificado".
    """

    max_intentos = 3
    for intento in range(max_intentos):
        try:
            response = model.generate_content(prompt)
            resultado = response.text.strip()
            # Limpieza
            resultado = resultado.replace("$", "").replace("USD", "").replace(",", "").split(".")[0]
            
            time.sleep(2) 
            return resultado

        except Exception as e:
            error_msg = str(e)
            
            # Si es error de cuota (429) o servidor (503)
            if "429" in error_msg or "Quota" in error_msg or "503" in error_msg:
                print(f"⏳ Google ocupado (Intento {intento+1}/{max_intentos}). Esperando 5 seg...")
                time.sleep(5)
                
            # Si es error 404 (Modelo no encontrado), cambiamos al backup
            elif "404" in error_msg:
                 print("⚠️ Modelo no encontrado, cambiando a 'models/gemini-pro'...")
                 # Como ya declaramos 'global model' al inicio, esto ya funciona:
                 model = genai.GenerativeModel('models/gemini-pro')
                 time.sleep(1)
            
            else:
                print(f"⚠️ Error desconocido IA: {e}")
                return "Error IA"
    
    return "Error IA"

# --- PRUEBA ---
if __name__ == "__main__":
    print(f"🤖 Probando con modelo inicial: {MODEL_NAME}")
    prueba = "Se necesita desarrollador joven, pago de 200 dólares a la semana más beneficios."
    print(f"Texto: {prueba}")
    print(f"💰 Salario detectado: {extraer_salario_con_ia(prueba)}")