from fastapi import APIRouter, Query
from app.services.ofertas_service import get_ofertas, get_oferta_by_id

router = APIRouter(prefix="/ofertas", tags=["ofertas"])


@router.get("")
def list_ofertas(
    rol: str | None = None,
    locacion: str | None = None,
    seniority: str | None = None,
    plataforma: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    salario_min: float | None = None,
    salario_max: float | None = None,
    habilidades: list[str] | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    data, total = get_ofertas(
        rol=rol,
        locacion=locacion,
        seniority=seniority,
        plataforma=plataforma,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        salario_min=salario_min,
        salario_max=salario_max,
        habilidades=habilidades,
        page=page,
        limit=limit,
    )
    total_pages = (total + limit - 1) // limit if total else 1
    return {"data": data, "total": total, "page": page, "total_pages": total_pages}


@router.get("/{id}")
def oferta_by_id(id: str):
    oferta = get_oferta_by_id(id)
    if oferta is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return oferta
