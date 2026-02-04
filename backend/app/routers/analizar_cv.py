"""Análisis de CV: extrae texto del archivo, usa embeddings para comparar con el mercado."""
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from app.database import get_supabase
from app.utils import parse_habilidades, extraer_texto_archivo
from app.embeddings import embed_text
from app.llm import validar_es_cv
from collections import Counter

router = APIRouter(tags=["analizar-cv"])

SIMILARITY_THRESHOLD = 0.27
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/analizar-cv")
async def analizar_cv(
    archivo: UploadFile = File(...),
    rol_objetivo: str | None = Form(None),
):
    # 1. Validar tipo de archivo
    filename = archivo.filename or ""
    if not (filename.lower().endswith(".pdf") or filename.lower().endswith(".docx")):
        raise HTTPException(400, "Solo se aceptan archivos PDF o DOCX")

    contenido = await archivo.read()
    if len(contenido) > MAX_FILE_SIZE:
        raise HTTPException(400, "El archivo supera el límite de 10 MB")

    if len(contenido) == 0:
        raise HTTPException(400, "El archivo está vacío")

    # 2. Extraer texto del CV
    try:
        texto_cv = extraer_texto_archivo(contenido, filename)
    except Exception as e:
        raise HTTPException(422, f"No se pudo extraer texto del archivo: {e}")

    texto_cv = texto_cv.replace("\n", " ").strip()
    if not texto_cv or len(texto_cv) < 20:
        raise HTTPException(422, "El archivo no contiene texto suficiente para analizar")

    # 3. Validación con Groq: confirmar que el documento es un CV/Hoja de Vida
    texto_muestra = texto_cv[:1000]
    es_cv, tipo_documento = validar_es_cv(texto_muestra)
    if not es_cv and tipo_documento:
        raise HTTPException(
            422,
            f"Solo se aceptan Currículum Vitae u Hojas de Vida. El documento subido parece ser un {tipo_documento}.",
        )

    # 4. Generar embedding del CV con embed_text (embeddings.py)
    try:
        cv_embedding = embed_text(texto_cv)
    except Exception as e:
        raise HTTPException(500, f"Error al procesar el CV: {e}")

    if not cv_embedding:
        raise HTTPException(500, "No se pudo generar el perfil del CV")

    sb = get_supabase()

    # 5. Búsqueda semántica: encontrar ofertas similares al CV
    matched_jobs = []
    try:
        params = {
            "query_embedding": cv_embedding,
            "match_threshold": SIMILARITY_THRESHOLD,
            "match_count": 200,
        }
        rpc_response = sb.rpc("match_jobs_ids", params).execute()
        matched_ids = [row["id"] for row in (rpc_response.data or [])]

        if matched_ids:
            r = sb.table("jobs_clean").select("habilidades, seniority").in_("id", matched_ids).execute()
            matched_jobs = r.data or []
    except Exception as e:
        print(f"RPC match_jobs_ids falló (columna embedding puede no existir): {e}")
        # Fallback: obtener todas las habilidades del mercado
        r = sb.table("jobs_clean").select("habilidades, seniority").limit(500).execute()
        matched_jobs = r.data or []

    # 6. Agregar habilidades del mercado desde ofertas coincidentes
    todas_habilidades = []
    seniorities: list[str] = []
    for row in matched_jobs:
        habs = parse_habilidades(row.get("habilidades"))
        todas_habilidades.extend(h.strip().upper() for h in habs if h.strip())
        s = row.get("seniority")
        if s and str(s).lower() not in ("no especificado", ""):
            seniorities.append(str(s).lower())

    top_skills = [nombre for nombre, _ in Counter(todas_habilidades).most_common(30)]

    # 7. Clasificar: detectadas (aparecen en CV) vs faltantes (del mercado, no en CV)
    texto_cv_upper = texto_cv.upper()
    habilidades_detectadas = []
    habilidades_faltantes = []
    for skill in top_skills:
        # El skill está en el CV si la palabra (o variante) aparece en el texto
        if skill in texto_cv_upper or skill.replace(" ", "") in texto_cv_upper.replace(" ", ""):
            habilidades_detectadas.append(skill)
        else:
            habilidades_faltantes.append(skill)

    # Limitar cantidad mostrada
    habilidades_detectadas = habilidades_detectadas[:12]
    habilidades_faltantes = habilidades_faltantes[:8]

    # 8. Compatibilidad: % de skills del mercado que el CV tiene
    total_relevante = len(habilidades_detectadas) + len(habilidades_faltantes)
    if total_relevante > 0:
        compatibilidad_porcentaje = min(95, int(len(habilidades_detectadas) / total_relevante * 100) + 20)
    else:
        compatibilidad_porcentaje = 50

    # 9. Nivel seniority: el más común en ofertas similares
    if seniorities:
        nivel_seniority = Counter(seniorities).most_common(1)[0][0]
        # Normalizar a junior | semi-senior | senior
        if "senior" in nivel_seniority and "semi" not in nivel_seniority:
            nivel_seniority = "senior"
        elif "semi" in nivel_seniority:
            nivel_seniority = "semi-senior"
        elif "junior" in nivel_seniority or "trainee" in nivel_seniority:
            nivel_seniority = "junior"
        else:
            nivel_seniority = "semi-senior"
    else:
        nivel_seniority = "semi-senior"

    # 10. Resumen y sugerencias
    if habilidades_faltantes:
        resumen = f"Tu perfil se alinea con la demanda del mercado IT en Ecuador. Detectamos {len(habilidades_detectadas)} habilidades relevantes. Para mejorar tu compatibilidad, considera desarrollar: {', '.join(habilidades_faltantes[:3])}."
    else:
        resumen = "Tu perfil tiene buena alineación con la demanda del mercado IT. Mantén tus habilidades actualizadas."

    sugerencias = [
        {"titulo": "Cuantifica tus logros", "descripcion": "Incluye métricas en tu CV (ej: reducción de tiempo, aumento de usuarios)."},
        {"titulo": "Keywords del mercado", "descripcion": f"Habilidades más demandadas: {', '.join(top_skills[:8])}."},
        {"titulo": "Formato de contacto", "descripcion": "Incluye LinkedIn y ubicación (Ej: Quito, EC)."},
    ]
    if habilidades_faltantes:
        sugerencias.append({
            "titulo": "Prioriza estas habilidades",
            "descripcion": f"Considera aprender o profundizar: {', '.join(habilidades_faltantes[:5])}.",
        })

    return {
        "compatibilidad_porcentaje": compatibilidad_porcentaje,
        "nivel_seniority": nivel_seniority,
        "resumen": resumen,
        "habilidades_detectadas": habilidades_detectadas,
        "habilidades_faltantes": habilidades_faltantes,
        "sugerencias": sugerencias,
    }
