"""
DevRadar Backend - FastAPI

Conecta con Supabase (jobs_clean) y expone API para el frontend.
Carga variables de entorno desde .env en la raíz del proyecto.
"""
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env desde la raíz del proyecto (no desde backend/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import ofertas, estadisticas, listas, comparar, analizar_cv, reporte_ia, chat

app = FastAPI(
    title="DevRadar API",
    description="API para datos del mercado IT Ecuador (scraper + jobs_clean)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://217.216.89.228:8080",
        "http://localhost:8080"  # Agregado para permitir el frontend en el puerto 8080
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prefijo /api para coincidir con frontend (VITE_API_URL + /api)
app.include_router(ofertas.router, prefix="/api")
app.include_router(estadisticas.router, prefix="/api")
app.include_router(listas.router, prefix="/api")
app.include_router(comparar.router, prefix="/api")
app.include_router(analizar_cv.router, prefix="/api")
app.include_router(reporte_ia.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "DevRadar API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
