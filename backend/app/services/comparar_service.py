"""
Comparación de tecnologías A y B con consultas SQL sobre habilidades.
Equivalente a: SELECT COUNT(*), AVG(sueldo) FROM jobs_clean WHERE habilidades ILIKE '%tecnologia%'
Veredicto y cosas buenas generados por el LLM según estos datos.
Tendencia histórica: conteo real por mes usando fecha_publicacion (solo meses con datos).
"""
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from app.database import get_supabase
from app.utils import parse_fecha_publicacion
from app.llm import generar_veredicto_comparacion

MESES_ABREV = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
MAX_MESES_TENDENCIA = 12


def _contar_y_promedio_sueldo_por_habilidad(sb, tecnologia: str) -> tuple[int, float]:
    """
    Número exacto de vacantes activas donde habilidades contiene la tecnología (ILIKE).
    Equivalente SQL: SELECT count(*), avg(sueldo) FROM jobs_clean WHERE habilidades ILIKE '%tecnologia%'
    """
    patron = f"%{tecnologia.strip()}%" if tecnologia else "%"
    r = sb.table("jobs_clean").select("sueldo").ilike("habilidades", patron).execute()
    rows = r.data or []

    count = len(rows)
    sueldos = []
    for row in rows:
        s = row.get("sueldo")
        if s is not None and s != "":
            try:
                sueldos.append(float(s))
            except (TypeError, ValueError):
                pass
    salario_promedio = round(sum(sueldos) / len(sueldos), 2) if sueldos else 0.0
    return count, salario_promedio


def _tendencia_historica_real(sb, tecnologia_a: str, tecnologia_b: str, periodo_meses: int) -> list[dict]:
    """
    Construye tendencia_historica con conteo por mes usando el mismo ILIKE que vacantes_activas.
    Consulta la BD con .ilike("habilidades", "%tecnologia%") para cada habilidad y agrupa por mes
    según fecha_publicacion, así el criterio de conteo concuerda exactamente con el número de vacantes.
    """
    ahora = datetime.now(timezone.utc)
    desde = ahora - timedelta(days=periodo_meses * 31)
    patron_a = f"%{(tecnologia_a or '').strip()}%" if (tecnologia_a or "").strip() else "%"
    patron_b = f"%{(tecnologia_b or '').strip()}%" if (tecnologia_b or "").strip() else "%"

    # Mismo ILIKE que _contar_y_promedio_sueldo_por_habilidad: conteo con LIKE en la BD
    r_a = sb.table("jobs_clean").select("fecha_publicacion").ilike("habilidades", patron_a).execute()
    r_b = sb.table("jobs_clean").select("fecha_publicacion").ilike("habilidades", patron_b).execute()
    rows_a = r_a.data or []
    rows_b = r_b.data or []

    # (year, month) -> (count_a, count_b)
    por_mes: dict[tuple[int, int], tuple[int, int]] = defaultdict(lambda: (0, 0))

    for row in rows_a:
        fp = parse_fecha_publicacion(row.get("fecha_publicacion"))
        if fp is None or fp < desde or fp > ahora:
            continue
        key = (fp.year, fp.month)
        ca, cb = por_mes[key]
        por_mes[key] = (ca + 1, cb)

    for row in rows_b:
        fp = parse_fecha_publicacion(row.get("fecha_publicacion"))
        if fp is None or fp < desde or fp > ahora:
            continue
        key = (fp.year, fp.month)
        ca, cb = por_mes[key]
        por_mes[key] = (ca, cb + 1)

    if not por_mes:
        return []

    ordenados = sorted(por_mes.keys())
    return [
        {
            "mes": f"{MESES_ABREV[ym[1] - 1]} {ym[0]}",
            "valor_a": por_mes[ym][0],
            "valor_b": por_mes[ym][1],
        }
        for ym in ordenados
    ]


def comparar_tecnologias(
    tecnologia_a: str,
    tecnologia_b: str,
    periodo_meses: int = 12,
) -> dict:
    """
    Compara dos tecnologías con consultas por habilidades (ILIKE).
    Vacantes activas = conteo exacto de filas donde habilidades ILIKE '%tecnologia%'.
    El LLM genera resúmenes, cosas buenas y veredicto según estos datos.
    """
    sb = get_supabase()

    count_a, salario_a = _contar_y_promedio_sueldo_por_habilidad(sb, tecnologia_a)
    count_b, salario_b = _contar_y_promedio_sueldo_por_habilidad(sb, tecnologia_b)

    try:
        r_total = sb.table("jobs_clean").select("id", count="exact").limit(1).execute()
        total_ofertas = getattr(r_total, "count", None)
        if total_ofertas is None:
            r_all = sb.table("jobs_clean").select("id").execute()
            total_ofertas = len(r_all.data or [])
    except Exception:
        total_ofertas = 0

    cuota_a = round((count_a / total_ofertas * 100), 1) if total_ofertas else 0.0
    cuota_b = round((count_b / total_ofertas * 100), 1) if total_ofertas else 0.0

    conclusion_llm = generar_veredicto_comparacion(
        tecnologia_a=tecnologia_a,
        tecnologia_b=tecnologia_b,
        count_a=count_a,
        count_b=count_b,
        salario_a=salario_a,
        salario_b=salario_b,
        cuota_a=cuota_a,
        cuota_b=cuota_b,
    )

    tendencia = _tendencia_historica_real(
        sb, tecnologia_a, tecnologia_b, min(periodo_meses, MAX_MESES_TENDENCIA)
    )

    return {
        "tecnologia_a": {
            "nombre": tecnologia_a,
            "tipo": "Tecnología",
            "salario_promedio": salario_a,
            "salario_variacion": 0,
            "vacantes_activas": count_a,
            "cuota_mercado": cuota_a,
            "tendencia": "estable",
        },
        "tecnologia_b": {
            "nombre": tecnologia_b,
            "tipo": "Tecnología",
            "salario_promedio": salario_b,
            "salario_variacion": 0,
            "vacantes_activas": count_b,
            "cuota_mercado": cuota_b,
            "tendencia": "estable",
        },
        "tendencia_historica": tendencia,
        "conclusion": {
            "ganador": "neutral",
            "resumen_a": conclusion_llm["resumen_a"],
            "resumen_b": conclusion_llm["resumen_b"],
            "resumen_neutral": conclusion_llm["resumen_neutral"],
            "cosas_buenas_a": conclusion_llm.get("cosas_buenas_a", []),
            "cosas_buenas_b": conclusion_llm.get("cosas_buenas_b", []),
            "veredicto_final": conclusion_llm.get("veredicto_final", ""),
        },
    }
