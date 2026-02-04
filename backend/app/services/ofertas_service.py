"""
Servicio de ofertas laborales desde jobs_clean.
Filtro de fechas por fecha_publicacion (TEXT con formatos mixtos: solo fecha o fecha+hora).
"""
from datetime import datetime, timezone
from app.database import get_supabase
from app.utils import row_to_oferta, parse_habilidades, parse_fecha_publicacion

# Límite de filas a traer cuando se filtra por fecha (fecha_publicacion se filtra en Python)
MAX_ROWS_WHEN_DATE_FILTER = 5000


def _rango_fechas_datetime(fecha_desde: str | None, fecha_hasta: str | None) -> tuple[datetime | None, datetime | None]:
    """Convierte fecha_desde/fecha_hasta a datetime UTC para comparar con fecha_publicacion."""
    desde_dt = hasta_dt = None
    if fecha_desde and len(fecha_desde) >= 10:
        try:
            y, m, d = int(fecha_desde[:4]), int(fecha_desde[5:7]), int(fecha_desde[8:10])
            desde_dt = datetime(y, m, d, 0, 0, 0, tzinfo=timezone.utc)
        except (ValueError, IndexError):
            pass
    if fecha_hasta and len(fecha_hasta) >= 10:
        try:
            y, m, d = int(fecha_hasta[:4]), int(fecha_hasta[5:7]), int(fecha_hasta[8:10])
            hasta_dt = datetime(y, m, d, 23, 59, 59, tzinfo=timezone.utc)
        except (ValueError, IndexError):
            pass
    return desde_dt, hasta_dt


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
    """Lista ofertas con filtros. Retorna (lista, total). Fechas se filtran por fecha_publicacion."""
    sb = get_supabase()
    filtrar_por_fecha = bool(fecha_desde or fecha_hasta)
    desde_dt, hasta_dt = _rango_fechas_datetime(fecha_desde, fecha_hasta) if filtrar_por_fecha else (None, None)

    q = sb.table("jobs_clean").select("*", count="exact")

    if rol:
        q = q.ilike("rol_busqueda", f"%{rol}%")
    if locacion:
        q = q.ilike("locacion", f"%{locacion}%")
    if plataforma:
        q = q.eq("plataforma", plataforma)
    # No filtrar por created_at cuando el usuario pide rango de fechas: usamos fecha_publicacion
    if not filtrar_por_fecha:
        if fecha_desde:
            q = q.gte("created_at", fecha_desde)
        if fecha_hasta:
            q = q.lte("created_at", fecha_hasta)
    if salario_min is not None:
        q = q.gte("sueldo", salario_min)
    if salario_max is not None:
        q = q.lte("sueldo", salario_max)

    if filtrar_por_fecha:
        # Traer más filas para filtrar por fecha_publicacion en Python (columna TEXT con formatos mixtos)
        q = q.order("created_at", desc=True)
        q = q.limit(MAX_ROWS_WHEN_DATE_FILTER)
        r = q.execute()
        all_rows = r.data or []
        rows_with_fp = [(row, parse_fecha_publicacion(row.get("fecha_publicacion"))) for row in all_rows]
        filtered = [row for row, fp in rows_with_fp if fp is not None
                    and (desde_dt is None or fp >= desde_dt)
                    and (hasta_dt is None or fp <= hasta_dt)]
        filtered.sort(key=lambda row: (parse_fecha_publicacion(row.get("fecha_publicacion")) or datetime.min.replace(tzinfo=timezone.utc)), reverse=True)
        total = len(filtered)
        offset = (page - 1) * limit
        rows = filtered[offset:offset + limit]
    else:
        q = q.order("created_at", desc=True)
        offset = (page - 1) * limit
        q = q.range(offset, offset + limit - 1)
        r = q.execute()
        rows = r.data or []
        total = getattr(r, "count", None)
        if total is None:
            total = len(rows)

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
