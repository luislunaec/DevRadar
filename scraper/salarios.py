import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

# 1. CARGA DE VARIABLES (Soporte para ambos nombres por seguridad)
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR CRÍTICO: No se encontró GOOGLE_API_KEY ni GEMINI_API_KEY en el .env")

genai.configure(api_key=API_KEY)

# 2. CONFIGURACIÓN DEL MODELO (Usamos tu versión potente)
# Como vimos en tu lista, tienes el 2.5 Flash, lo usamos de primario.
MODEL_NAME = 'models/gemini-2.5-flash'

try:
    model = genai.GenerativeModel(MODEL_NAME)
except:
    print("⚠️ El modelo 2.5 no respondió, cambiando a Gemini Pro...")
    model = genai.GenerativeModel('models/gemini-pro')

def extraer_salario_con_ia(texto_oferta):
    global model
    
    # Filtro rápido: Si el texto es muy corto, devolvemos "No especificado" directo
    if not texto_oferta or len(str(texto_oferta)) < 15: 
        return "No especificado"

    prompt = f"""
    Analiza esta oferta de trabajo de Ecuador y extrae el SALARIO MENSUAL BASE.
    TEXTO: '''{texto_oferta[:2500]}'''
    
    REGLAS:
    1. Si es por hora, multiplica por 160.
    2. Si es diario, multiplica por 22.
    3. Si es semanal, multiplica por 4.
    4. "Sueldo Básico" = 460 USD.
    5. Si es un rango (ej: 800-1000), saca el promedio (900).
    6. Si dice "Salario Competitivo", "A convenir" o no hay cifras, responde "No especificado".
    
    Responde SOLO el número entero limpio (ej: 800) o la frase "No especificado".
    """

    max_intentos = 3
    for intento in range(max_intentos):
        try:
            response = model.generate_content(prompt)
            resultado = response.text.strip()
            
            # Limpieza agresiva de símbolos
            resultado = resultado.replace("$", "").replace("USD", "").replace(",", "").split(".")[0]
            
            # Validación: Si la respuesta no parece un número ni es la frase clave
            if not resultado.isdigit() and "No especificado" not in resultado:
                return "No especificado"

            time.sleep(1.5) # Pausa de cortesía para Google
            return resultado

        except Exception as e:
            error_msg = str(e)
            
            # Manejo inteligente de errores
            if "429" in error_msg or "Quota" in error_msg or "Resource" in error_msg:
                print(f"⏳ Google saturado (Intento {intento+1}). Esperando 10 seg...")
                time.sleep(10)
                
            elif "404" in error_msg or "Not Found" in error_msg:
                print("🔄 Modelo no encontrado, cambiando a 'models/gemini-pro'...")
                model = genai.GenerativeModel('models/gemini-pro')
                time.sleep(1)
            
            else:
                # Si es otro error raro, mejor saltamos esta oferta
                return "No especificado"
    
    return "No especificado"

# --- PRUEBA PARA VERIFICAR QUE FUNCIONA ---
if __name__ == "__main__":
    print(f"🚀 Probando módulo de salarios con modelo: {MODEL_NAME}")
    prueba = "Buscamos desarrollador Full Stack. Ofrecemos sueldo básico ecuatoriano más bonos de desempeño."
    print(f"📝 Texto: {prueba}")
    print(f"💰 Resultado IA: {extraer_salario_con_ia(prueba)}")