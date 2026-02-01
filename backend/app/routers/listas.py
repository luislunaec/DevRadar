"""Listas para filtros: roles, ubicaciones, habilidades populares."""
from fastapi import APIRouter, Query
from app.database import get_supabase
from app.utils import parse_habilidades
from collections import Counter

router = APIRouter(tags=["listas"])


@router.get("/roles-disponibles")
def roles_disponibles():
    sb = get_supabase()
    r = sb.table("jobs_clean").select("rol_busqueda").execute()
    rows = r.data or []
    roles = sorted({str(x.get("rol_busqueda", "")).strip() for x in rows if x.get("rol_busqueda")})
    return [r for r in roles if r]


@router.get("/ubicaciones")
def ubicaciones():
    sb = get_supabase()
    r = sb.table("jobs_clean").select("locacion").execute()
    rows = r.data or []
    locs = sorted({str(x.get("locacion", "")).strip() for x in rows if x.get("locacion")})
    return [l for l in locs if l]


@router.get("/habilidades-populares")
def habilidades_populares(limit: int = Query(50, ge=1, le=200)):
    sb = get_supabase()
    r = sb.table("jobs_clean").select("habilidades").execute()
    rows = r.data or []
    counter: Counter = Counter()
    for row in rows:
        for h in parse_habilidades(row.get("habilidades")):
            if h:
                counter[h.strip()] += 1
    return [nombre for nombre, _ in counter.most_common(limit)]
