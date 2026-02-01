"""
Servicio de ofertas laborales desde jobs_clean.
"""
from datetime import datetime, timedelta
from app.database import get_supabase
from app.utils import row_to_oferta, parse_habilidades


def get_ofertas(
    rol: str | None = None,
    locacion: str | None = None,
    seniority: str | None = None,
    plataforma: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    salario_min: float | None = None,
    salario_max: float | None = None,
    habilidades: list[str] | None = None,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[dict], int]:
    """Lista ofertas con filtros. Retorna (lista, total)."""
    sb = get_supabase()
    q = sb.table("jobs_clean").select("*", count="exact")

    if rol:
        q = q.ilike("rol_busqueda", f"%{rol}%")
    if locacion:
        q = q.ilike("locacion", f"%{locacion}%")
    if plataforma:
        q = q.eq("plataforma", plataforma)
    if fecha_desde:
        q = q.gte("created_at", fecha_desde)
    if fecha_hasta:
        q = q.lte("created_at", fecha_hasta)
    if salario_min is not None:
        q = q.gte("sueldo", salario_min)
    if salario_max is not None:
        q = q.lte("sueldo", salario_max)

    q = q.order("created_at", desc=True)
    offset = (page - 1) * limit
    q = q.range(offset, offset + limit - 1)
    r = q.execute()
    rows = r.data or []
    # Supabase/PostgREST con count=exact puede devolver total en el response
    total = getattr(r, "count", None)
    if total is None:
        total = len(rows)

    # Filtro por seniority (si existe columna) o por habilidades en cliente
    result = []
    for row in rows:
        d = row_to_oferta(row)
        if seniority and d.get("seniority") and d["seniority"] != seniority:
            continue
        if habilidades:
            habs = set(h.lower() for h in d.get("habilidades", []))
            if not any(s.lower() in habs for s in habilidades):
                continue
        result.append(d)

    # Si filtramos por seniority/habilidades en cliente, total puede no coincidir; aproximamos
    if not seniority and not habilidades:
        return result, total
    return result, total if len(result) == len(rows) else len(result)


def get_oferta_by_id(id_str: str) -> dict | None:
    """Obtiene una oferta por id."""
    sb = get_supabase()
    try:
        r = sb.table("jobs_clean").select("*").eq("id", int(id_str)).limit(1).execute()
        if r.data and len(r.data) > 0:
            return row_to_oferta(r.data[0])
    except (ValueError, TypeError):
        pass
    return None
