"""Análisis de CV: stub que usa habilidades del mercado para sugerencias."""
from fastapi import APIRouter, File, UploadFile, Form
from app.database import get_supabase
from app.utils import parse_habilidades
from collections import Counter

router = APIRouter(tags=["analizar-cv"])


@router.post("/analizar-cv")
async def analizar_cv(
    archivo: UploadFile = File(...),
    rol_objetivo: str | None = Form(None),
):
    # Stub: no parseamos PDF/DOCX aquí; devolvemos análisis basado en habilidades populares del mercado
    # En producción se usaría un servicio de IA para extraer habilidades del CV
    sb = get_supabase()
    r = sb.table("jobs_clean").select("habilidades").execute()
    rows = r.data or []
    counter: Counter = Counter()
    for row in rows:
        for h in parse_habilidades(row.get("habilidades")):
            if h:
                counter[h.strip()] += 1
    top_skills = [s for s, _ in counter.most_common(20)]

    # Simular habilidades detectadas (en real sería del CV) y faltantes
    habilidades_detectadas = top_skills[:6] if len(top_skills) >= 6 else top_skills.copy()
    habilidades_faltantes = [s for s in top_skills if s not in habilidades_detectadas][:5]

    return {
        "compatibilidad_porcentaje": 70,
        "nivel_seniority": "semi-senior",
        "resumen": "Tu perfil se alinea con la demanda del mercado IT en Ecuador. Mejora las habilidades faltantes para aumentar tu compatibilidad.",
        "habilidades_detectadas": habilidades_detectadas,
        "habilidades_faltantes": habilidades_faltantes,
        "sugerencias": [
            {"titulo": "Cuantifica tus logros", "descripcion": "Incluye métricas en tu CV (ej: reducción de tiempo, aumento de usuarios)."},
            {"titulo": "Keywords del mercado", "descripcion": f"Habilidades más demandadas en el mercado: {', '.join(top_skills[:8])}."},
            {"titulo": "Formato de contacto", "descripcion": "Incluye LinkedIn y ubicación (Ej: Quito, EC)."},
        ],
    }
