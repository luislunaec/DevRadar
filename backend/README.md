# DevRadar Backend

API FastAPI que se conecta a Supabase (tabla `jobs_clean`) y sirve datos al frontend.

## Variables de entorno

Crea un archivo `.env` en `backend/` con:

- `SUPABASE_URL`: URL del proyecto Supabase (igual que el scraper)
- `SUPABASE_KEY`: service role key o anon key
- `GROQ_API_KEY`: API key de Groq para el veredicto neutral en comparar-tecnologías (opcional; si falta, se usa texto fijo)

Para que la comparación use **búsqueda semántica** (embeddings como el limpiador), en Supabase la tabla `jobs_clean` debe tener la columna `embedding vector(384)`. Si no existe, el comparador usa fallback por nombre en la columna `habilidades`. Ver comentarios en `scraper/db/create_tables.sql` para el `ALTER TABLE` y el índice.

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
