"""
LLM Groq para veredictos objetivos y validaciones.
Requiere GROQ_API_KEY en .env (cargado desde main.py).
"""
import json
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def validar_es_cv(texto: str) -> tuple[bool, str | None]:
    """
    Valida si el documento es un CV DE TECNOLOGÍA usando Groq.
    Filtra perfiles no-tech (Chefs, Abogados, etc.).
    """
    if not GROQ_API_KEY:
        # Si no hay API key, dejamos pasar por defecto para no bloquear
        return True, None

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=GROQ_API_KEY,
        )

        # --- PROMPT ESTRICTO DE RECLUTADOR IT ---
        system = """Eres un Reclutador Técnico Senior (IT Recruiter) estricto.
Tu trabajo es filtrar hojas de vida para una empresa de tecnología.

Analiza el texto y responde ÚNICAMENTE en JSON con estas claves:
- es_cv: boolean
- tipo_documento: string | null

REGLAS DE ACEPTACIÓN (es_cv: true):
1. El documento ES UN CURRICULUM VITAE (Hoja de Vida).
2. Y ADEMÁS, el perfil es del área de TECNOLOGÍA (Desarrollador, Datos, QA, Redes, Ciberseguridad, Soporte Técnico, etc.).
3. O ES ESTUDIANTE de carreras afines (Sistemas, Software, Informática).

REGLAS DE RECHAZO (es_cv: false):
- NO es un CV (es un artículo, receta, contrato, tarea, factura).
- ES un CV pero de OTRA PROFESIÓN NO RELACIONADA (Ej: Abogado, Chef, Vendedor de Seguros, Contador, Psicólogo, Chofer).

Si rechazas porque es otra profesión, en 'tipo_documento' pon: "CV de [Profesión detectada] (No es perfil IT)".
Si rechazas porque no es un CV, pon qué es (Ej: "Receta de cocina").
"""

        texto_muestra = texto[:1500].strip()
        human = f"""Analiza este documento y decide si pasa el filtro IT:

---
{texto_muestra}
---

Responde solo con el JSON."""

        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=human)])
        text = response.content if hasattr(response, "content") else str(response)
        text = text.strip()

        # Limpieza robusta del JSON
        if "```" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]
        
        data = json.loads(text)

        es_cv = data.get("es_cv", False)
        tipo = data.get("tipo_documento")

        return bool(es_cv), None if es_cv else str(tipo)

    except Exception as e:
        print(f"Validación CV con Groq falló: {e}")
        # Fail Open: Si la IA falla, dejamos pasar el archivo
        return True, None


def _fallback_veredicto(
    tecnologia_a: str,
    tecnologia_b: str,
    count_a: int,
    count_b: int,
    salario_a: float,
    salario_b: float,
    cuota_a: float,
    cuota_b: float,
) -> dict:
    return {
        "resumen_a": f"{tecnologia_a} aparece en {count_a} ofertas, con salario promedio ${salario_a:,.0f}. Cuota {cuota_a}%.",
        "resumen_b": f"{tecnologia_b} aparece en {count_b} ofertas, con salario promedio ${salario_b:,.0f}. Cuota {cuota_b}%.",
        "resumen_neutral": "La comparación se basa en ofertas reales. Interpreta los datos según tu contexto.",
        "cosas_buenas_a": [],
        "cosas_buenas_b": [],
        "veredicto_final": "Ambas tecnologías tienen presencia. Elige según tu rol y objetivos.",
    }


def generar_veredicto_comparacion(
    tecnologia_a: str,
    tecnologia_b: str,
    count_a: int,
    count_b: int,
    salario_a: float,
    salario_b: float,
    cuota_a: float,
    cuota_b: float,
) -> dict:
    """
    Genera con Groq: resúmenes, cosas buenas y veredicto.
    """
    if not GROQ_API_KEY:
        return _fallback_veredicto(
            tecnologia_a, tecnologia_b, count_a, count_b, salario_a, salario_b, cuota_a, cuota_b
        )

    try:
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=GROQ_API_KEY,
        )

        system = """Eres un analista del mercado laboral IT. Redactas conclusiones OBJETIVAS y NEUTRALES.
No declares ganador. No favorezcas a una tecnología sobre otra.
Responde ÚNICAMENTE en JSON con estas claves (en español):
- resumen_a: 1-2 oraciones sobre la primera tecnología.
- resumen_b: 1-2 oraciones sobre la segunda tecnología.
- resumen_neutral: 2-3 oraciones que resuman ambas de forma imparcial.
- cosas_buenas_a: array de 2 a 4 strings (puntos fuertes objetivos).
- cosas_buenas_b: array de 2 a 4 strings (puntos fuertes objetivos).
- veredicto_final: 1-2 oraciones de cierre neutral."""

        human = f"""Comparación (datos reales):

Tecnología A: {tecnologia_a}
- Ofertas: {count_a}
- Salario: ${salario_a:,.0f}
- Cuota: {cuota_a}%

Tecnología B: {tecnologia_b}
- Ofertas: {count_b}
- Salario: ${salario_b:,.0f}
- Cuota: {cuota_b}%

Genera el JSON. Solo JSON, sin markdown."""

        response = llm.invoke([SystemMessage(content=system), HumanMessage(content=human)])
        text = response.content if hasattr(response, "content") else str(response)

        text = text.strip()
        if "```" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                text = text[start:end]
        data = json.loads(text)

        def as_string_list(v):
            if isinstance(v, list):
                return [str(x).strip() for x in v if x]
            return []

        return {
            "resumen_a": data.get("resumen_a", ""),
            "resumen_b": data.get("resumen_b", ""),
            "resumen_neutral": data.get("resumen_neutral", ""),
            "cosas_buenas_a": as_string_list(data.get("cosas_buenas_a", [])),
            "cosas_buenas_b": as_string_list(data.get("cosas_buenas_b", [])),
            "veredicto_final": data.get("veredicto_final", ""),
        }
    except Exception:
        return _fallback_veredicto(
            tecnologia_a, tecnologia_b, count_a, count_b, salario_a, salario_b, cuota_a, cuota_b
        )