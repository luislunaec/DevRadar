from fastapi import APIRouter, Query
from app.services.estadisticas_service import (
    get_estadisticas_mercado,
    get_tecnologias_demandadas,
    get_distribucion_seniority,
)

router = APIRouter(prefix="/estadisticas", tags=["estadisticas"])


@router.get("/mercado")
def estadisticas_mercado(
    rol: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
):
    return get_estadisticas_mercado(rol=rol, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)


@router.get("/tecnologias")
def tecnologias_demandadas(
    limit: int = Query(10, ge=1, le=50),
    rol: str | None = None,
):
    return get_tecnologias_demandadas(limit=limit, rol=rol)


@router.get("/seniority")
def distribucion_seniority(rol: str | None = None):
    return get_distribucion_seniority(rol=rol)
