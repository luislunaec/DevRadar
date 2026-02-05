"""
Helper para conexión a Supabase - Producción Blindada
"""
import os
import re
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Cargamos el archivo .env a la memoria de Python
load_dotenv()

# 2. El "Recadero": Traemos los valores del .env a variables de Python
# AQUÍ NO PONEMOS LA URL, la instrucción os.getenv la busca solita
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 3. Validación de seguridad
if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR CRÍTICO: No se encontraron SUPABASE_URL o SUPABASE_KEY en el .env")
    print("👉 Revisa que el archivo .env exista en la raíz del proyecto.")
    exit(1)

# 4. Inicializamos el cliente oficial de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def limpiar_valor_para_supabase(value, campo_tipo='text'):
    """Limpia un valor para que sea compatible con Supabase (Evita errores de tipos)"""
    if value is None:
        return None
    
    # Manejar el fastidioso NaN de los DataFrames de Pandas
    if isinstance(value, float) and pd.isna(value):
        return None
    
    if isinstance(value, str):
        value_lower = value.lower().strip()
        # Si el texto dice literalmente 'nan' o está vacío, lo tratamos como Nulo
        if value_lower in ['nan', 'none', 'null', '', 'no especificado']:
            return None if campo_tipo == 'numeric' else ''
        
        if campo_tipo == 'numeric':
            try:
                # Extrae solo números y puntos (limpia $, comas de miles, etc.)
                cleaned = re.sub(r'[^\d.]', '', value_lower.replace(',', '.'))
                return float(cleaned) if cleaned else None
            except:
                return None
        return value
    
    if campo_tipo == 'numeric':
        try:
            return float(value) if not pd.isna(value) else None
        except:
            return None
    
    return str(value).strip() if value else ''

def guardar_oferta_cruda(datos):
    """Guarda una oferta cruda en la tabla jobs_raw usando UPSERT"""
    try:
        # Preparamos el diccionario limpio para la base de datos
        datos_limpios = {
            'plataforma': limpiar_valor_para_supabase(datos.get('plataforma'), 'text') or 'desconocida',
            'rol_busqueda': limpiar_valor_para_supabase(datos.get('rol_busqueda'), 'text') or '',
            'fecha_publicacion': limpiar_valor_para_supabase(datos.get('fecha_publicacion'), 'text') or '',
            'oferta_laboral': limpiar_valor_para_supabase(datos.get('oferta_laboral'), 'text') or 'Sin Título',
            'locacion': limpiar_valor_para_supabase(datos.get('locacion'), 'text') or 'Ecuador',
            'descripcion': limpiar_valor_para_supabase(datos.get('descripcion'), 'text') or '',
            'sueldo': limpiar_valor_para_supabase(datos.get('sueldo'), 'numeric'),
            'compania': limpiar_valor_para_supabase(datos.get('compania'), 'text') or 'Confidencial',
            'url_publicacion': limpiar_valor_para_supabase(datos.get('url_publicacion'), 'text') or '',
            # Importante: Marcamos como procesado = False para que la IA la limpie después
            'processed': False 
        }
        
        # Validación mínima: Si no hay URL, no podemos guardarlo
        if not datos_limpios['url_publicacion']:
            return False
        
        # UPSERT: Si la URL ya existe, actualiza los datos. Si no, crea la fila.
        supabase.table('jobs_raw').upsert(
            datos_limpios, 
            on_conflict='url_publicacion'
        ).execute()
        
        return True

    except Exception as e:
        print(f"⚠️ Error en Supabase Helper: {str(e)[:100]}")
        return False