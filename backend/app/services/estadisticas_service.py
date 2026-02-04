from collections import Counter
from app.database import get_supabase
from app.utils import parse_habilidades
from app.services.ai_service import get_embedding 

# Umbral de similitud. 
SIMILARITY_THRESHOLD = 0.27

def _aplicar_filtro_semantico(query_builder, rol: str | None):
    """
    Inyecta filtro vectorial si hay rol, usando HuggingFace embeddings.
    """
    if not rol:
        return query_builder

    # 1. Vectorizamos el rol
    vector_busqueda = get_embedding(rol)

    if not vector_busqueda:
        print("Fallo al generar embedding, usando fallback vacio")
        return query_builder.eq("id", -1)

    sb = get_supabase()
    
    # 2. RPC a Supabase (match_jobs_ids)
    params = {
        "query_embedding": vector_busqueda,
        "match_threshold": SIMILARITY_THRESHOLD,
        "match_count": 1000
    }
    
    try:
        rpc_response = sb.rpc("match_jobs_ids", params).execute()
    except Exception as e:
        print(f"Error en RPC match_jobs_ids: {e}")
        return query_builder.eq("id", -1)
    
    # 3. Extraer IDs
    matched_ids = [row['id'] for row in rpc_response.data] if rpc_response.data else []

    if not matched_ids:
        return query_builder.eq("id", -1)

    return query_builder.in_("id", matched_ids)


# --- HELPERS PARA FECHAS (Para no repetir código) ---
def _aplicar_filtro_fecha(query_builder, fecha_desde: str | None, fecha_hasta: str | None):
    if fecha_desde:
        query_builder = query_builder.gte("created_at", fecha_desde)
    if fecha_hasta:
        query_builder = query_builder.lte("created_at", fecha_hasta)
    return query_builder


def get_estadisticas_mercado(
    rol: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
) -> dict:
    sb = get_supabase()
    q = sb.table("jobs_clean").select("id, sueldo, created_at, rol_busqueda")

    # Filtros
    q = _aplicar_filtro_semantico(q, rol)
    q = _aplicar_filtro_fecha(q, fecha_desde, fecha_hasta) # ✅ Fecha agregada

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


def get_tecnologias_demandadas(
    limit: int = 10, 
    rol: str | None = None,
    fecha_desde: str | None = None, # 🆕 Agregado
    fecha_hasta: str | None = None  # 🆕 Agregado
) -> list[dict]:
    sb = get_supabase()
    q = sb.table("jobs_clean").select("habilidades, rol_busqueda, created_at") # Traemos created_at
    
    # Filtros
    q = _aplicar_filtro_semantico(q, rol)
    q = _aplicar_filtro_fecha(q, fecha_desde, fecha_hasta) # ✅ AHORA SÍ FILTRA FECHA

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


def get_distribucion_seniority(
    rol: str | None = None,
    fecha_desde: str | None = None, # 🆕 Agregado
    fecha_hasta: str | None = None  # 🆕 Agregado
) -> dict:
    sb = get_supabase()
    q = sb.table("jobs_clean").select("seniority, rol_busqueda, created_at") # Traemos created_at
    
    # Filtros
    q = _aplicar_filtro_semantico(q, rol)
    q = _aplicar_filtro_fecha(q, fecha_desde, fecha_hasta) # ✅ AHORA SÍ FILTRA FECHA
    
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