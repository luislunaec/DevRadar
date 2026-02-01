from fastapi import APIRouter
from pydantic import BaseModel
from app.services.comparar_service import comparar_tecnologias

router = APIRouter(tags=["comparar"])


class CompararBody(BaseModel):
    tecnologia_a: str
    tecnologia_b: str
    periodo_meses: int = 12


@router.post("/comparar-tecnologias")
def comparar(body: CompararBody):
    return comparar_tecnologias(
        tecnologia_a=body.tecnologia_a,
        tecnologia_b=body.tecnologia_b,
        periodo_meses=body.periodo_meses,
    )
