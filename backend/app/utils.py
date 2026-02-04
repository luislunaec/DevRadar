"""
Utilidades para mapear filas de jobs_clean al formato API.
"""
import re
from datetime import datetime, timezone
from typing import Any
import io


def parse_fecha_publicacion(texto: str | None) -> datetime | None:
    """
    Parsea fecha_publicacion (TEXT en jobs_clean): acepta solo fecha o fecha+hora.
    Formatos: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, YYYY-MM-DDTHH:MM:SSZ, YYYY-MM-DD HH:MM:SS,
    DD/MM/YYYY, DD-MM-YYYY. Retorna datetime en UTC o None si no se puede parsear.
    """
    if not texto or not isinstance(texto, str):
        return None
    texto = texto.strip()
    if not texto:
        return None
    # ISO con hora: 2024-01-15T14:30:00 o 2024-01-15T14:30:00Z o 2024-01-15T14:30:00.123Z
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})[T\s](\d{1,2}):(\d{2})(?::(\d{2}))?(?:\.(\d+))?(?:Z)?", texto)
    if m:
        try:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            h, mi = int(m.group(4)), int(m.group(5))
            s = int(m.group(6)) if m.group(6) else 0
            return datetime(y, mo, d, h, mi, s, tzinfo=timezone.utc)
        except ValueError:
            pass
    # Solo fecha ISO: 2024-01-15
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})(?:\s|$|Z)", texto)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
        except ValueError:
            pass
    # DD/MM/YYYY o DD-MM-YYYY
    m = re.match(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", texto)
    if m:
        try:
            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)), tzinfo=timezone.utc)
        except ValueError:
            pass
    return None


def extraer_texto_archivo(contenido: bytes, filename: str) -> str:
    """
    Extrae texto de PDF o DOCX según extensión del archivo.
    """
    name_lower = (filename or "").lower()
    if name_lower.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(contenido))
        return " ".join(page.extract_text() or "" for page in reader.pages)
    if name_lower.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(contenido))
        return " ".join(p.text for p in doc.paragraphs)
    raise ValueError("Solo se soportan archivos PDF y DOCX")


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
