"""
LLM Groq para veredictos objetivos (mismo enfoque que limpiador).
Requiere GROQ_API_KEY en .env.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


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
        "resumen_a": f"{tecnologia_a} aparece en {count_a} ofertas (búsqueda por palabras), con salario promedio ${salario_a:,.0f}. Cuota de mercado {cuota_a}%.",
        "resumen_b": f"{tecnologia_b} aparece en {count_b} ofertas (búsqueda por palabras), con salario promedio ${salario_b:,.0f}. Cuota de mercado {cuota_b}%.",
        "resumen_neutral": "La comparación se basa en el conteo exacto de ofertas que mencionan cada tecnología. Interpreta los datos según tu contexto (rol, industria, seniority).",
        "cosas_buenas_a": [],
        "cosas_buenas_b": [],
        "veredicto_final": "Ambas tecnologías tienen presencia en el mercado. Elige según tu rol, industria y objetivos.",
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
    Genera con Groq: resúmenes, cosas buenas de cada tecnología y veredicto final objetivo.
    """
    if not GROQ_API_KEY:
        return _fallback_veredicto(
            tecnologia_a, tecnologia_b, count_a, count_b, salario_a, salario_b, cuota_a, cuota_b
        )

    import json

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
- resumen_a: 1-2 oraciones sobre la primera tecnología (datos de ofertas y salario).
- resumen_b: 1-2 oraciones sobre la segunda tecnología (datos de ofertas y salario).
- resumen_neutral: 2-3 oraciones que resuman ambas de forma imparcial.
- cosas_buenas_a: array de 2 a 4 strings; cada uno es un punto fuerte o ventaja objetiva de la tecnología A en el mercado laboral (ej: "Alta demanda en startups", "Ecosistema maduro").
- cosas_buenas_b: array de 2 a 4 strings; puntos fuertes objetivos de la tecnología B.
- veredicto_final: 1-2 oraciones de cierre neutral que ayuden al lector a decidir (ej: "Ambas son opciones sólidas; considera el tipo de empresa y el stack del equipo")."""

        human = f"""Comparación en el mercado laboral (datos reales: conteo exacto de ofertas que mencionan cada tecnología por búsqueda por palabras en título, descripción y habilidades):

Tecnología A: {tecnologia_a}
- Número de ofertas que la mencionan: {count_a}
- Salario promedio en esas ofertas: ${salario_a:,.0f}
- Cuota de mercado: {cuota_a}%

Tecnología B: {tecnologia_b}
- Número de ofertas que la mencionan: {count_b}
- Salario promedio en esas ofertas: ${salario_b:,.0f}
- Cuota de mercado: {cuota_b}%

Genera el JSON con resumen_a, resumen_b, resumen_neutral, cosas_buenas_a, cosas_buenas_b y veredicto_final. Solo JSON, sin markdown."""

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
