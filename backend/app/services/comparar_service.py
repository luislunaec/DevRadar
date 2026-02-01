"""
Comparación de dos tecnologías/habilidades basada en jobs_clean.
"""
from collections import defaultdict
from app.database import get_supabase
from app.utils import parse_habilidades


def comparar_tecnologias(
    tecnologia_a: str,
    tecnologia_b: str,
    periodo_meses: int = 12,
) -> dict:
    """Compara dos tecnologías: vacantes, salario promedio, cuota de mercado. Tendencia histórica simplificada."""
    sb = get_supabase()
    r = sb.table("jobs_clean").select("habilidades, sueldo, created_at, rol_busqueda").execute()
    rows = r.data or []

    def normalizar(n: str) -> str:
        return n.strip().lower()

    a_key = normalizar(tecnologia_a)
    b_key = normalizar(tecnologia_b)

    sueldos_a: list[float] = []
    sueldos_b: list[float] = []
    count_a = 0
    count_b = 0

    for row in rows:
        habs = parse_habilidades(row.get("habilidades"))
        habs_norm = [normalizar(h) for h in habs]
        tiene_a = any(a_key in h or h in a_key for h in habs_norm)
        tiene_b = any(b_key in h or h in b_key for h in habs_norm)

        try:
            s = row.get("sueldo")
            if s is not None and s != "":
                sal = float(s)
                if tiene_a:
                    sueldos_a.append(sal)
                if tiene_b:
                    sueldos_b.append(sal)
        except (TypeError, ValueError):
            pass
        if tiene_a:
            count_a += 1
        if tiene_b:
            count_b += 1

    total = len(rows)
    salario_a = sum(sueldos_a) / len(sueldos_a) if sueldos_a else 0
    salario_b = sum(sueldos_b) / len(sueldos_b) if sueldos_b else 0
    cuota_a = (count_a / total * 100) if total else 0
    cuota_b = (count_b / total * 100) if total else 0

    # Tendencia histórica: simplificada (meses genéricos con valores proporcionales)
    meses_nombres = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    n_meses = min(periodo_meses, 12)
    tendencia = []
    for i in range(n_meses):
        # Valores aproximados basados en count_a/count_b
        base_a = count_a * (0.8 + (i / n_meses) * 0.4) if count_a else 0
        base_b = count_b * (0.8 + (i / n_meses) * 0.4) if count_b else 0
        tendencia.append({
            "mes": meses_nombres[i],
            "valor_a": int(base_a),
            "valor_b": int(base_b),
        })

    ganador = "neutral"
    if count_a > count_b and salario_a >= salario_b:
        ganador = "a"
    elif count_b > count_a and salario_b >= salario_a:
        ganador = "b"

    tipo_a = "Tecnología"
    tipo_b = "Tecnología"

    return {
        "tecnologia_a": {
            "nombre": tecnologia_a,
            "tipo": tipo_a,
            "salario_promedio": round(salario_a, 2),
            "salario_variacion": 0,
            "vacantes_activas": count_a,
            "cuota_mercado": round(cuota_a, 1),
            "tendencia": "estable",
        },
        "tecnologia_b": {
            "nombre": tecnologia_b,
            "tipo": tipo_b,
            "salario_promedio": round(salario_b, 2),
            "salario_variacion": 0,
            "vacantes_activas": count_b,
            "cuota_mercado": round(cuota_b, 1),
            "tendencia": "estable",
        },
        "tendencia_historica": tendencia,
        "conclusion": {
            "ganador": ganador,
            "resumen_a": f"{tecnologia_a} aparece en {count_a} ofertas. Salario promedio ${salario_a:,.0f}.",
            "resumen_b": f"{tecnologia_b} aparece en {count_b} ofertas. Salario promedio ${salario_b:,.0f}.",
            "resumen_neutral": "Ambas tecnologías tienen presencia en el mercado. La elección depende del rol y sector.",
        },
    }
