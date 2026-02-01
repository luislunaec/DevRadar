# DevRadar Backend

API FastAPI que se conecta a Supabase (tabla `jobs_clean`) y sirve datos al frontend.

## Variables de entorno

Copia las mismas que usa el scraper:

- `SUPABASE_URL`: URL del proyecto Supabase
- `SUPABASE_KEY`: service role key o anon key

Crea un archivo `.env` en `backend/` con esas variables.

## Instalación y ejecución

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000  
Docs: http://localhost:8000/docs

## Endpoints (prefijo `/api`)

- `GET /api/ofertas` – Lista de ofertas con filtros
- `GET /api/ofertas/{id}` – Detalle de oferta
- `GET /api/estadisticas/mercado` – Estadísticas del mercado
- `GET /api/estadisticas/tecnologias` – Top tecnologías demandadas
- `GET /api/estadisticas/seniority` – Distribución por seniority
- `POST /api/comparar-tecnologias` – Comparar dos tecnologías
- `GET /api/roles-disponibles` – Roles para filtros
- `GET /api/ubicaciones` – Ubicaciones
- `GET /api/habilidades-populares` – Habilidades populares
- `POST /api/analizar-cv` – Análisis de CV (stub con datos del mercado)
- `POST /api/generar-reporte` – Reporte IA desde datos reales
