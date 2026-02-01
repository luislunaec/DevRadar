"""
Helper para conexión a Supabase
"""
import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ ERROR: Faltan SUPABASE_URL o SUPABASE_KEY en el .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def limpiar_valor_para_supabase(value, campo_tipo='text'):
    """Limpia un valor para que sea compatible con Supabase"""
    if value is None:
        return None
    
    # Manejar NaN de pandas
    if isinstance(value, float) and pd.isna(value):
        return None
    
    # Manejar strings que dicen 'nan' o 'none'
    if isinstance(value, str):
        value_lower = value.lower().strip()
        if value_lower in ['nan', 'none', 'null', '', 'no especificado']:
            return None if campo_tipo == 'numeric' else ''
        # Si es numérico pero viene como string, intentar convertir
        if campo_tipo == 'numeric':
            try:
                # Limpiar caracteres no numéricos
                cleaned = value_lower.replace('$', '').replace('usd', '').replace(',', '').strip()
                if cleaned:
                    return float(cleaned)
            except (ValueError, AttributeError):
                pass
            return None
        return value
    
    # Para números, asegurar que sea float o int
    if campo_tipo == 'numeric':
        if isinstance(value, (int, float)):
            if pd.isna(value):
                return None
            return float(value)
        return None
    
    # Para texto, convertir a string
    return str(value) if value else ''

def guardar_oferta_cruda(datos):
    """Guarda una oferta cruda en la tabla jobs_raw"""
    try:
        # Limpiar y formatear datos según el esquema de la tabla
        datos_limpios = {
            'plataforma': limpiar_valor_para_supabase(datos.get('plataforma'), 'text') or 'computrabajo',
            'rol_busqueda': limpiar_valor_para_supabase(datos.get('rol_busqueda'), 'text') or '',
            'fecha_publicacion': limpiar_valor_para_supabase(datos.get('fecha_publicacion'), 'text') or '',
            'oferta_laboral': limpiar_valor_para_supabase(datos.get('oferta_laboral'), 'text') or 'Sin Título',
            'locacion': limpiar_valor_para_supabase(datos.get('locacion'), 'text') or 'Ecuador',
            'descripcion': limpiar_valor_para_supabase(datos.get('descripcion'), 'text') or '',
            'sueldo': limpiar_valor_para_supabase(datos.get('sueldo'), 'numeric'),
            'compania': limpiar_valor_para_supabase(datos.get('compania'), 'text') or 'Confidencial',
            'url_publicacion': limpiar_valor_para_supabase(datos.get('url_publicacion'), 'text') or ''
        }
        
        # Validar que url_publicacion no esté vacío
        if not datos_limpios['url_publicacion']:
            return False
        
        # Validar que plataforma y oferta_laboral no estén vacíos (NOT NULL en la tabla)
        if not datos_limpios['plataforma'] or not datos_limpios['oferta_laboral']:
            return False
        
        supabase.table('jobs_raw').upsert(datos_limpios, on_conflict='url_publicacion').execute()
        return True
    except Exception as e:
        error_msg = str(e)
        # Si es error de tabla no encontrada, mostrar mensaje más claro
        if 'jobs_raw' in error_msg or 'PGRST205' in error_msg:
            print(f"⚠️ Error: La tabla 'jobs_raw' no existe en Supabase. Ejecuta create_tables.sql primero.")
        elif 'duplicate key' in error_msg.lower() or 'unique constraint' in error_msg.lower():
            # URL duplicada, no es un error crítico
            return True
        else:
            print(f"⚠️ Error guardando oferta: {error_msg[:150]}")
        return False
