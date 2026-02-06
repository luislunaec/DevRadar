DevRadar
========

**DevRadar** es una plataforma para el **análisis del mercado laboral TI en Ecuador**, centrada en las **habilidades y tecnologías más demandadas**. El proyecto recopila ofertas de empleo desde múltiples portales, limpia y enriquece los datos con IA, los almacena en Supabase y expone estadísticas, búsquedas y herramientas avanzadas a través de una aplicación web.

### Características principales

- **Scraping de ofertas de empleo** desde varios portales (Computrabajo, Jooble, LinkedIn).
- **Limpieza y enriquecimiento de datos con IA** (extracción de habilidades, normalización de campos).
- **Almacenamiento en Supabase (PostgreSQL)** con soporte de búsqueda semántica mediante embeddings.
- **API REST con FastAPI** para exponer:
  - Listado y detalle de ofertas.
  - Estadísticas de mercado (tecnologías, seniority, ubicaciones, etc.).
  - Comparación de tecnologías con IA.
  - Análisis de CVs (PDF/DOCX).
  - Reportes automáticos con IA.
  - Chatbot con contexto de ofertas laborales.
- **Frontend en React + Vite + Tailwind + shadcn/ui** para visualizar el mercado, comparar skills y usar las herramientas de IA.
- **Docker Compose + GitHub Actions** para despliegue automatizado en un servidor (VPS).

---

### Arquitectura del proyecto

El repositorio es un **monorepo** con tres componentes principales:

- **`backend/`**: API REST construida con FastAPI.
- **`frontend/`**: aplicación web en React/TypeScript.
- **`scraper/`**: servicio de scraping y procesamiento de datos.

Servicios externos:

- **Supabase (PostgreSQL)** para almacenamiento de datos y vectores.
- **Groq API** (opcional) para análisis y comparación de tecnologías.
- **Google Generative AI (Gemini)** (opcional) para tareas de IA en el scraper.
- **Redis** (opcional) para historial de chat.

---

### Estructura de carpetas

```text
DevRadar/
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── routers/      # Endpoints de la API
│   │   ├── services/     # Lógica de negocio
│   │   ├── database.py
│   │   ├── embeddings.py
│   │   └── llm.py
│   ├── main.py           # Punto de entrada FastAPI
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/             # Aplicación React
│   ├── src/
│   │   ├── pages/        # Páginas principales (dashboard, comparación, CV, etc.)
│   │   ├── components/   # Componentes UI
│   │   ├── services/     # Cliente de la API
│   │   ├── hooks/
│   │   └── test/         # Tests con Vitest
│   ├── package.json
│   ├── vite.config.ts
│   ├── vitest.config.ts
│   ├── tailwind.config.ts
│   └── Dockerfile
│
├── scraper/              # Servicio de scraping
│   ├── scrapers/         # Scrapers por portal
│   ├── limpiador/        # Limpieza y enriquecimiento con IA
│   ├── db/               # Scripts SQL y helper de Supabase
│   ├── main.py           # Pipeline principal
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/
│   └── DEPLOY.md         # Detalles de despliegue
│
├── .github/workflows/    # CI/CD con GitHub Actions
├── docker-compose.yml    # Orquestación de servicios
└── README.md
```

---

### Tecnologías utilizadas

**Frontend**

- React 18 + TypeScript
- Vite
- Tailwind CSS + shadcn/ui (Radix UI)
- React Router DOM
- TanStack Query (React Query)
- Recharts
- Vitest (testing)

**Backend**

- FastAPI (Python 3.11)
- Uvicorn
- Supabase (cliente Python)
- LangChain (Groq, HuggingFace)
- Sentence Transformers (embeddings)
- PyPDF, python-docx (análisis de CVs)
- Redis (opcional)

**Scraper**

- Python 3.11
- Selenium + undetected-chromedriver
- BeautifulSoup4
- Pandas
- Requests
- Supabase
- Google Generative AI (Gemini)
- LangChain

**Infraestructura**

- Supabase (PostgreSQL + extensión vector)
- Docker y Docker Compose
- GitHub Actions para CI/CD

---

### Requisitos previos

- **Node.js** 18+ (recomendado 20+ / 22+ según Dockerfile del frontend).
- **Python** 3.11.
- **Docker** y **Docker Compose** (para entorno con contenedores y despliegue).
- Cuenta/proyecto en **Supabase** configurado.
- Opcional:
  - Clave de API de **Groq** (`GROQ_API_KEY`).
  - Clave de **Google AI / Gemini** (`GOOGLE_API_KEY`).
  - Instancia de **Redis** para historial de chat.

---

### Variables de entorno

Crear un archivo `.env` en la **raíz** del proyecto con algo similar a:

```env
# Supabase (obligatorio)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key-o-anon-key

# Groq API (opcional - comparación de tecnologías)
GROQ_API_KEY=tu-groq-api-key

# Google AI / Gemini (opcional - scraper)
GOOGLE_API_KEY=tu-google-api-key

# Redis (opcional - historial de chat)
REDIS_URL=redis://localhost:6379

# URL pública del API (para frontend / producción)
PUBLIC_API_URL=http://tu-servidor:8000/api
```

El **backend** y el **scraper** leen este `.env` desde la raíz del proyecto.

---

### Instalación y ejecución en desarrollo (sin Docker)

#### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

#### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Por defecto, Vite sirve la app en `http://localhost:5173` (o el puerto configurado).

#### Scraper

```bash
cd scraper
pip install -r requirements.txt
python main.py        # Últimos 2 días por defecto
python main.py 5      # Últimos 5 días
```

El scraper recoge ofertas, las limpia y las almacena en las tablas de Supabase (`jobs_raw`, `jobs_clean`, `jobs`).

---

### Ejecución con Docker Compose

Para levantar backend y frontend con Docker Compose:

```bash
docker compose up -d backend frontend
```

Para ejecutar el scraper como un job puntual:

```bash
docker compose run --rm scraper          # Últimos 2 días
docker compose run --rm scraper 5        # Últimos 5 días
```

Para reconstruir imágenes y actualizar servicios:

```bash
docker compose up -d --build backend frontend
```

Para detener los servicios:

```bash
docker compose down
```

---

### Scripts y comandos útiles

**Frontend**

- `npm run dev` – servidor de desarrollo.
- `npm run build` – build de producción.
- `npm run preview` – previsualizar el build.
- `npm run lint` – ejecutar ESLint.
- `npm run test` – ejecutar tests con Vitest.
- `npm run test:watch` – tests en modo watch.

**Backend**

- `uvicorn main:app --reload --host 0.0.0.0 --port 8000` – desarrollo.
- `uvicorn main:app --host 0.0.0.0 --port 8000` – producción (u otro servidor ASGI).

**Scraper**

- `python main.py` – ejecuta el pipeline de scraping (últimos 2 días).
- `python main.py <días>` – ejecuta scraping de los últimos `<días>` días.

---

### Endpoints principales de la API

El backend expone endpoints bajo el prefijo `/api`, entre ellos:

- `GET /api/ofertas` – listado de ofertas con filtros.
- `GET /api/ofertas/{id}` – detalle de una oferta.
- `GET /api/estadisticas/mercado` – estadísticas generales del mercado.
- `GET /api/estadisticas/tecnologias` – tecnologías más demandadas.
- `GET /api/estadisticas/seniority` – distribución por seniority.
- `POST /api/comparar-tecnologias` – compara tecnologías usando datos + IA.
- `GET /api/roles-disponibles` – catálogo de roles.
- `GET /api/ubicaciones` – ubicaciones más frecuentes.
- `GET /api/habilidades-populares` – habilidades demandadas.
- `POST /api/analizar-cv` – análisis de CV (PDF/DOCX).
- `POST /api/generar-reporte` – generación de reportes con IA.
- `POST /api/chat` – chatbot con contexto de ofertas laborales.

La documentación interactiva se puede consultar en `/docs`.

---

### Despliegue y CI/CD

El proyecto incluye un flujo de CI/CD con **GitHub Actions** (`.github/workflows/deploy.yml`) para desplegar en un servidor remoto (VPS) vía SSH:

1. Genera un archivo `.env` en el servidor usando **GitHub Secrets**.
2. Conecta al VPS por SSH.
3. Clona o actualiza el repositorio.
4. Copia el `.env` al directorio de despliegue.
5. Ejecuta `docker compose up -d --build backend frontend`.

Secrets típicos:

- `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY`
- `SUPABASE_URL`, `SUPABASE_KEY`, `PUBLIC_API_URL`
- Opcionales: `GROQ_API_KEY`, `REDIS_URL`, `DEPLOY_PATH`

Más detalles en `docs/DEPLOY.md`.

---

### Estado del proyecto

DevRadar combina **scraping**, **análisis de datos** y **modelos de lenguaje** para ofrecer una vista actualizada del mercado laboral TI, ayudando a:

- Desarrolladores que desean alinear sus habilidades con la demanda real.
- Empresas que buscan entender tendencias tecnológicas.
- Equipos que quieren dashboards y reportes de mercado generados con IA.

Este README resume la configuración actual del proyecto; revisa los `README` específicos de `backend/`, `frontend/` y `scraper/` para detalles más técnicos de cada módulo.
