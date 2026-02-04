from fastapi import APIRouter, Query
from app.services.estadisticas_service import (
    get_estadisticas_mercado,
    get_tecnologias_demandadas,
    get_distribucion_seniority,
)
from app.services.ai_service import validar_termino_con_ia

router = APIRouter(prefix="/estadisticas", tags=["estadisticas"])

# --- FUNCIÓN AUXILIAR PARA NO REPETIR CÓDIGO ---
def obtener_rol_validado(rol: str | None):
    """
    Valida el rol con IA. 
    Retorna: (es_valido, rol_corregido, mensaje_error)
    """
    if not rol:
        return True, None, None # Si es búsqueda global, pasa.

    validacion = validar_termino_con_ia(rol)
    
    if not validacion.is_tech:
        return False, None, "No es tech"
    
    # Si hay corrección (ej: jaba -> Java), usamos esa
    nuevo_rol = validacion.suggested_correction if validacion.suggested_correction else rol
    return True, nuevo_rol, None


@router.get("/mercado")
def estadisticas_mercado(
    rol: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
):
    # 1. Validamos
    es_valido, rol_final, error = obtener_rol_validado(rol)
    
    if not es_valido:
            # Respuesta vacía para /mercado
            return {
                "total_ofertas": 0,
                "salario_promedio": 0,
                "nivel_demanda": "bajo",  # <--- CAMBIA ESTO (antes decía "Búsqueda Inválida")
                "mensaje": f"😅 '{rol}' no parece ser tecnología.",
            }

    # 2. Buscamos con el rol corregido (o None si es global)
    return get_estadisticas_mercado(rol=rol_final, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)


@router.get("/tecnologias")
def tecnologias_demandadas(
    limit: int = Query(10, ge=1, le=50),
    rol: str | None = None,
):
    # 1. Validamos también aquí
    es_valido, rol_final, error = obtener_rol_validado(rol)
    
    if not es_valido:
        return [] # Retorna lista vacía -> Gráfica vacía

    return get_tecnologias_demandadas(limit=limit, rol=rol_final)


@router.get("/seniority")
def distribucion_seniority(rol: str | None = None):
    # 1. Validamos también aquí
    es_valido, rol_final, error = obtener_rol_validado(rol)
    
    if not es_valido:
        return [] # Retorna lista vacía -> Gráfica vacía (o objeto vacío según tu frontend)

    return get_distribucion_seniority(rol=rol_final)