"""
Utilidades para mapear filas de jobs_clean al formato API.
"""
from typing import Any


def parse_habilidades(h: Any) -> list[str]:
    """Convierte habilidades (TEXT en DB: comma-separated o JSON string) a lista."""
    if h is None or (isinstance(h, str) and not h.strip()):
        return []
    if isinstance(h, list):
        return [str(x).strip() for x in h if x]
    s = str(h).strip()
    if s.startswith("["):
        try:
            import json
            out = json.loads(s)
            return [str(x).strip() for x in out if x]
        except Exception:
            pass
    return [x.strip() for x in s.split(",") if x.strip()]


def row_to_oferta(row: dict) -> dict:
    """Convierte una fila de jobs_clean al formato OfertaLaboral del frontend."""
    return {
        "id": str(row.get("id", "")),
        "plataforma": str(row.get("plataforma", "")),
        "rol_busqueda": str(row.get("rol_busqueda", "")),
        "fecha_publicacion": str(row.get("fecha_publicacion", "")),
        "oferta_laboral": str(row.get("oferta_laboral", "")),
        "locacion": str(row.get("locacion", "")),
        "descripcion": str(row.get("descripcion", "")),
        "sueldo": str(row["sueldo"]) if row.get("sueldo") is not None else None,
        "compania": str(row.get("compania", "")),
        "habilidades": parse_habilidades(row.get("habilidades")),
        "url_publicacion": str(row.get("url_publicacion", "")),
        "created_at": row.get("created_at", ""),
        "seniority": row.get("seniority"),
    }
