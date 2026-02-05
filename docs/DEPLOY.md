# Despliegue DevRadar en VPS con GitHub Actions

## Variables de entorno (.env)

Copia esto en un archivo `.env` en la raíz del proyecto (para desarrollo local o para generarlo en el workflow). **No subas `.env` a Git.**

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key-o-anon-key
GROQ_API_KEY=
REDIS_URL=redis://localhost:6379
PUBLIC_API_URL=http://217.216.89.228:8000/api
```

## Requisitos en el VPS (217.216.89.228 o el que uses)

- **Docker** y **Docker Compose** (v2) instalados.
- Usuario con acceso SSH por clave (no solo contraseña).
- Puerto 22 abierto para SSH; puertos 8000 (API) y 8080 (frontend) abiertos para tráfico entrante.

## GitHub Secrets (obligatorios y opcionales)

Configura en el repositorio: **Settings → Secrets and variables → Actions**.

### Obligatorios para el deploy

| Secret            | Descripción |
|-------------------|-------------|
| `SSH_HOST`        | IP o dominio del VPS (ej: `217.216.89.228`). |
| `SSH_USER`        | Usuario SSH (ej: `root` o `ubuntu`). |
| `SSH_PRIVATE_KEY` | Contenido completo de la clave privada SSH (la que usas para `ssh -i clave user@host`). Sin contraseña o con passphrase configurada en el job si la tiene. |
| `SUPABASE_URL`     | URL del proyecto Supabase (ej: `https://xxxx.supabase.co`). |
| `SUPABASE_KEY`     | Service role key o anon key de Supabase. |
| `PUBLIC_API_URL`   | URL pública del backend para el frontend (ej: `http://217.216.89.228:8000/api`). Debe ser la URL que verá el navegador. |

### Opcionales

| Secret       | Descripción |
|-------------|-------------|
| `GROQ_API_KEY` | API key de Groq para veredictos y comparación de tecnologías. Si no se pone, esas funciones usan texto fijo. |
| `REDIS_URL`    | URL de Redis para el historial del chat (ej: `redis://localhost:6379`). Si no hay Redis, el chat usa memoria. |

## Variable de repositorio (opcional)

| Variable       | Descripción |
|----------------|-------------|
| `DEPLOY_PATH`  | Ruta en el VPS donde se clona el repo y se ejecuta Docker. Por defecto: `/opt/devradar`. |

## Cómo funciona el workflow

1. **Push a `main`** o **ejecución manual** (Actions → Deploy to VPS → Run workflow).
2. Se genera un `.env` con los secrets y se copia al VPS.
3. Si es la primera vez, se clona el repo en `DEPLOY_PATH` (por defecto `/opt/devradar`).
4. Se hace `git fetch` + `git reset --hard origin/main` y se ejecuta `docker compose up -d --build backend frontend`.

El scraper **no** se levanta como servicio; puedes ejecutarlo a mano en el VPS:

```bash
cd /opt/devradar   # o tu DEPLOY_PATH
docker compose run --rm scraper          # últimos 2 días
docker compose run --rm scraper python main.py 5   # últimos 5 días
```

## Primera vez en el VPS

1. Instala Docker y Docker Compose (v2).
2. Crea el usuario que usarás en `SSH_USER` y configura la clave pública en `~/.ssh/authorized_keys`.
3. Si el repo es **privado**, en el VPS puedes configurar un deploy key o clonar una vez a mano con un token; el workflow actual asume que puede hacer `git clone https://github.com/...` (público) o que ya existe el directorio. Para repos privados, conviene clonar una vez en el servidor con un token y luego el workflow solo hará `git pull`.
4. Añade todos los secrets anteriores en GitHub y lanza el workflow.

## URLs tras el despliegue

- **Frontend:** `http://217.216.89.228:8080`
- **API / Docs:** `http://217.216.89.228:8000` y `http://217.216.89.228:8000/docs`

Asegúrate de que `PUBLIC_API_URL` en secrets sea exactamente `http://217.216.89.228:8000/api` (o tu dominio) para que el frontend llame bien al backend.
