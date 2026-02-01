"""
Modelos Pydantic alineados con el frontend (api.ts) y la tabla jobs_clean.
"""
from typing import Optional
from pydantic import BaseModel, Field


class OfertaLaboral(BaseModel):
    id: str
    plataforma: str = ""
    rol_busqueda: str = ""
    fecha_publicacion: str = ""
    oferta_laboral: str = ""
    locacion: str = ""
    descripcion: str = ""
    sueldo: Optional[str] = None
    compania: str = ""
    habilidades: list[str] = Field(default_factory=list)
    url_publicacion: str = ""
    created_at: str = ""
    seniority: Optional[str] = None  # junior | semi-senior | senior


class EstadisticasMercado(BaseModel):
    total_ofertas: int = 0
    ofertas_variacion_porcentaje: float = 0.0
    salario_promedio: float = 0.0
    salario_variacion_porcentaje: float = 0.0
    nivel_demanda: str = "medio"  # bajo | medio | alto
    nuevas_vacantes_porcentaje: float = 0.0


class TecnologiaDemanda(BaseModel):
    nombre: str
    porcentaje: float
    total_ofertas: int


class DistribucionSeniority(BaseModel):
    senior: int = 0
    semi_senior: int = 0
    junior: int = 0


class ComparacionTecnologias(BaseModel):
    tecnologia_a: dict
    tecnologia_b: dict
    tendencia_historica: list[dict]
    conclusion: dict


class AnalisisCV(BaseModel):
    compatibilidad_porcentaje: int
    nivel_seniority: str
    resumen: str
    habilidades_detectadas: list[str]
    habilidades_faltantes: list[str]
    sugerencias: list[dict]


class ReporteIA(BaseModel):
    region: str
    periodo: str
    actualizado: str
    resumen_ejecutivo: list[str]
    top_herramientas: list[dict]
    tendencia_crecimiento: list[dict]
