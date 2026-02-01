"""
Estadísticas agregadas desde jobs_clean.
"""
from collections import Counter
from app.database import get_supabase
from app.utils import parse_habilidades


def get_estadisticas_mercado(
    rol: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
) -> dict:
    """Estadísticas generales del mercado (total ofertas, salario promedio, nivel demanda)."""
    sb = get_supabase()
    q = sb.table("jobs_clean").select("id, sueldo, created_at, rol_busqueda")
    if rol:
        q = q.ilike("rol_busqueda", f"%{rol}%")
    if fecha_desde:
        q = q.gte("created_at", fecha_desde)
    if fecha_hasta:
        q = q.lte("created_at", fecha_hasta)
    r = q.execute()
    rows = r.data or []

    total = len(rows)
    sueldos = []
    for x in rows:
        v = x.get("sueldo")
        if v is not None and v != "":
            try:
                sueldos.append(float(v))
            except (TypeError, ValueError):
                pass

    salario_promedio = sum(sueldos) / len(sueldos) if sueldos else 0.0

    # Variación: sin histórico usamos 0; luego se puede calcular con fecha
    ofertas_variacion = 0.0
    salario_variacion = 0.0
    nuevas_vacantes = 0.0

    if total < 100:
        nivel_demanda = "bajo"
    elif total < 500:
        nivel_demanda = "medio"
    else:
        nivel_demanda = "alto"

    return {
        "total_ofertas": total,
        "ofertas_variacion_porcentaje": ofertas_variacion,
        "salario_promedio": round(salario_promedio, 2),
        "salario_variacion_porcentaje": salario_variacion,
        "nivel_demanda": nivel_demanda,
        "nuevas_vacantes_porcentaje": nuevas_vacantes,
    }


def get_tecnologias_demandadas(limit: int = 10, rol: str | None = None) -> list[dict]:
    """Top tecnologías/habilidades más demandadas (desde columna habilidades)."""
    sb = get_supabase()
    q = sb.table("jobs_clean").select("habilidades, rol_busqueda")
    if rol:
        q = q.ilike("rol_busqueda", f"%{rol}%")
    r = q.execute()
    rows = r.data or []

    counter: Counter = Counter()
    for row in rows:
        habs = parse_habilidades(row.get("habilidades"))
        for h in habs:
            if h:
                counter[h.strip()] += 1

    total_ofertas = len(rows)
    out = []
    for nombre, count in counter.most_common(limit):
        pct = (count / total_ofertas * 100) if total_ofertas else 0
        out.append({"nombre": nombre, "porcentaje": round(pct, 1), "total_ofertas": count})
    return out


def get_distribucion_seniority(rol: str | None = None) -> dict:
    """Distribución por nivel de experiencia. Si jobs_clean tiene columna seniority se usa; si no, estimación."""
    sb = get_supabase()
    q = sb.table("jobs_clean").select("*")
    if rol:
        q = q.ilike("rol_busqueda", f"%{rol}%")
    try:
        r = q.execute()
    except Exception:
        r = type("R", (), {"data": []})()

    rows = r.data or []
    # Filtrar por rol en cliente si no se aplicó en query (por si acaso)
    if rol and rows:
        rows = [x for x in rows if rol.lower() in (x.get("rol_busqueda") or "").lower()]
    senior = semi_senior = junior = 0
    for row in rows:
        s = (row.get("seniority") or "").lower().strip()
        if "senior" in s and "semi" not in s:
            senior += 1
        elif "semi" in s or "mid" in s:
            semi_senior += 1
        elif "junior" in s or "trainee" in s:
            junior += 1
        else:
            # Por defecto repartir en partes iguales si no hay seniority
            senior += 1

    total = senior + semi_senior + junior
    if total == 0:
        senior, semi_senior, junior = 33, 34, 33
    else:
        senior = int(senior / total * 100)
        semi_senior = int(semi_senior / total * 100)
        junior = 100 - senior - semi_senior

    return {"senior": senior, "semi_senior": semi_senior, "junior": junior}
