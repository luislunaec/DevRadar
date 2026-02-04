import re
from datetime import datetime, timezone
from collections import Counter
from app.database import get_supabase
from app.utils import parse_habilidades
from app.services.ai_service import get_embedding

# Umbral de similitud.
SIMILARITY_THRESHOLD = 0.27


def _parse_fecha_publicacion(texto: str | None) -> datetime | None:
    """Intenta extraer una fecha de fecha_publicacion (TEXT). Retorna None si no se puede."""
    if not texto or not isinstance(texto, str):
        return None
    texto = texto.strip()
    # Formato ISO o yyyy-MM-dd
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", texto)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
        except ValueError:
            pass
    # Formato dd/mm/yyyy o dd-mm-yyyy
    m = re.match(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", texto)
    if m:
        try:
            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)), tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def _fechas_iso_rango(fecha_desde: str | None, fecha_hasta: str | None) -> tuple[str | None, str | None]:
    """Convierte a ISO completo para PostgREST (UTC). Acepta yyyy-MM-dd o ISO con hora (ej. 24h)."""
    if not fecha_desde and not fecha_hasta:
        return None, None
    desde_iso = None
    hasta_iso = None
    if fecha_desde:
        if "T" in fecha_desde:
            desde_iso = fecha_desde.rstrip("Z") + "Z" if not fecha_desde.endswith("Z") else fecha_desde
        else:
            desde_iso = f"{fecha_desde}T00:00:00.000Z"
    if fecha_hasta:
        if "T" in fecha_hasta:
            hasta_iso = fecha_hasta.rstrip("Z") + "Z" if not fecha_hasta.endswith("Z") else fecha_hasta
        else:
            hasta_iso = f"{fecha_hasta}T23:59:59.999Z"
    return desde_iso, hasta_iso


def _aplicar_filtro_semantico(query_builder, rol: str | None):
    """
    Inyecta filtro vectorial si hay rol, usando HuggingFace embeddings.
    """
    if not rol:
        return query_builder

    # 1. Vectorizamos el rol (ej: "Python Backend") -> 384 floats
    vector_busqueda = get_embedding(rol)

    if not vector_busqueda:
        # Si falla el modelo local, retornamos filtro vacío seguro
        print("Fallo al generar embedding, usando fallback vacio")
        return query_builder.eq("id", -1)

    sb = get_supabase()
    
    # 2. RPC a Supabase (match_jobs_ids)
    params = {
        "query_embedding": vector_busqueda,
        "match_threshold": SIMILARITY_THRESHOLD,
        "match_count": 1000
    }
    
    # Ejecutamos la función RPC
    try:
        rpc_response = sb.rpc("match_jobs_ids", params).execute()
    except Exception as e:
        print(f"Error en RPC match_jobs_ids: {e}")
        return query_builder.eq("id", -1)
    
    # 3. Extraer IDs
    matched_ids = [row['id'] for row in rpc_response.data] if rpc_response.data else []

    if not matched_ids:
        # Si no hay coincidencias semánticas, devolver 0 resultados
        return query_builder.eq("id", -1)

    # Filtramos la tabla principal por los IDs encontrados
    return query_builder.in_("id", matched_ids)


def get_estadisticas_mercado(
    rol: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
) -> dict:
    sb = get_supabase()
    # Fechas en ISO completo para PostgREST (UTC), así el rango es correcto
    desde_iso, hasta_iso = _fechas_iso_rango(fecha_desde, fecha_hasta)

    q = sb.table("jobs_clean").select("id, sueldo, created_at, rol_busqueda")

    # Filtro por rol (semántico si hay rol)
    q = _aplicar_filtro_semantico(q, rol)

    if desde_iso:
        q = q.gte("created_at", desde_iso)
    if hasta_iso:
        q = q.lte("created_at", hasta_iso)

    r = q.execute()
    rows = r.data or []

    # Si hay filtro de fechas y salieron 0, intentar por fecha_publicacion (p. ej. datos cargados en lote)
    if (desde_iso or hasta_iso) and len(rows) == 0 and fecha_desde and fecha_hasta:
        q2 = sb.table("jobs_clean").select("id, sueldo, created_at, fecha_publicacion, rol_busqueda")
        q2 = _aplicar_filtro_semantico(q2, rol)
        r2 = q2.execute()
        all_rows = r2.data or []
        try:
            desde_dt = datetime(int(fecha_desde[:4]), int(fecha_desde[5:7]), int(fecha_desde[8:10]), 0, 0, 0, tzinfo=timezone.utc)
            hasta_dt = datetime(int(fecha_hasta[:4]), int(fecha_hasta[5:7]), int(fecha_hasta[8:10]), 23, 59, 59, tzinfo=timezone.utc)
        except (ValueError, IndexError):
            desde_dt = hasta_dt = None
        if desde_dt is not None and hasta_dt is not None:
            for row in all_rows:
                fp = _parse_fecha_publicacion(row.get("fecha_publicacion"))
                if fp is None:
                    continue
                if fp < desde_dt or fp > hasta_dt:
                    continue
                rows.append(row)

    total = len(rows)
    sueldos = []

    for x in rows:
        v = x.get("sueldo")
        if v is not None and v != "":
            try:
                sueldos.append(float(v))
            except (TypeError, ValueError):
                continue

    salario_promedio = (sum(sueldos) / len(sueldos)) if sueldos else 0.0

    if total < 20:
        nivel_demanda = "bajo"
    elif total < 100:
        nivel_demanda = "medio"
    else:
        nivel_demanda = "alto"

    return {
        "total_ofertas": total,
        "ofertas_variacion_porcentaje": 0.0, 
        "salario_promedio": round(salario_promedio, 2),
        "salario_variacion_porcentaje": 0.0,
        "nivel_demanda": nivel_demanda,
        "nuevas_vacantes_porcentaje": 0.0,
    }


def get_tecnologias_demandadas(limit: int = 10, rol: str | None = None) -> list[dict]:
    sb = get_supabase()
    q = sb.table("jobs_clean").select("habilidades, rol_busqueda")
    
    q = _aplicar_filtro_semantico(q, rol)
    
    r = q.execute()
    rows = r.data or []

    counter: Counter = Counter()
    total_validas = 0

    for row in rows:
        raw_habs = row.get("habilidades") 
        habs = parse_habilidades(raw_habs)
        
        if habs:
            total_validas += 1
            for h in habs:
                if h:
                    counter[h.strip().upper()] += 1

    out = []
    base_calc = total_validas if total_validas > 0 else 1

    for nombre, count in counter.most_common(limit):
        pct = (count / base_calc * 100)
        out.append({
            "nombre": nombre,
            "porcentaje": round(pct, 1),
            "total_ofertas": count
        })
    return out


def get_distribucion_seniority(rol: str | None = None) -> dict:
    sb = get_supabase()
    q = sb.table("jobs_clean").select("seniority, rol_busqueda")
    
    q = _aplicar_filtro_semantico(q, rol)
    
    r = q.execute()
    rows = r.data or []

    senior = 0
    semi_senior = 0
    junior = 0
    total = 0

    for row in rows:
        s = (row.get("seniority") or "").lower()
        
        if not s or s == "no especificado":
            continue
            
        total += 1
        if "senior" in s and "semi" not in s:
            senior += 1
        elif "semi" in s:
            semi_senior += 1
        elif "junior" in s or "trainee" in s:
            junior += 1
        else:
            semi_senior += 1

    if total == 0:
        return {"senior": 0, "semi_senior": 0, "junior": 0}

    return {
        "senior": int(senior / total * 100),
        "semi_senior": int(semi_senior / total * 100),
        "junior": int(junior / total * 100)
    }