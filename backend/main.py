"""
DevRadar Backend - FastAPI
Conecta con Supabase (jobs_clean) y expone API para el frontend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import ofertas, estadisticas, listas, comparar, analizar_cv, reporte_ia

app = FastAPI(
    title="DevRadar API",
    description="API para datos del mercado IT Ecuador (scraper + jobs_clean)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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


@app.get("/")
def root():
    return {"message": "DevRadar API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
