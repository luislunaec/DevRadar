-- =============================================================================
-- Script SQL para crear las tablas necesarias en Supabase
-- =============================================================================
-- Ejecuta este script en el SQL Editor de Supabase
-- Ve a: SQL Editor > New Query > Pega este código > Run

-- Tabla 1: jobs_raw (Datos crudos de los scrapers, solo append; pipeline incremental)
CREATE TABLE IF NOT EXISTS public.jobs_raw (
    id BIGSERIAL PRIMARY KEY,
    plataforma TEXT NOT NULL,
    rol_busqueda TEXT,
    fecha_publicacion TEXT,
    oferta_laboral TEXT NOT NULL,
    locacion TEXT,
    descripcion TEXT,
    sueldo NUMERIC,
    compania TEXT,
    url_publicacion TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed BOOLEAN NOT NULL DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Tabla 2: jobs_clean (Datos limpios con habilidades)
CREATE TABLE IF NOT EXISTS public.jobs_clean (
    id BIGSERIAL PRIMARY KEY,
    plataforma TEXT NOT NULL,
    rol_busqueda TEXT,
    fecha_publicacion TEXT,
    oferta_laboral TEXT NOT NULL,
    locacion TEXT,
    descripcion TEXT,
    sueldo NUMERIC,
    compania TEXT,
    habilidades TEXT,
    url_publicacion TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla 3: jobs (Datos finales con embeddings)
CREATE TABLE IF NOT EXISTS public.jobs (
    id BIGSERIAL PRIMARY KEY,
    plataforma TEXT NOT NULL,
    rol_busqueda TEXT,
    fecha_publicacion TEXT,
    oferta_laboral TEXT NOT NULL,
    locacion TEXT,
    descripcion TEXT,
    sueldo TEXT,
    compania TEXT,
    habilidades JSONB,
    url_publicacion TEXT UNIQUE NOT NULL,
    embedding vector(768),  -- Ajusta el tamaño según tu modelo de embedding
    job_clean_id BIGINT REFERENCES public.jobs_clean(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Si ya tenías jobs_clean con sueldo TEXT, migra con:
-- ALTER TABLE public.jobs_clean ALTER COLUMN sueldo TYPE NUMERIC USING NULL;

-- Si ya tenías jobs_raw sin processed, añade columnas para pipeline incremental:
-- ALTER TABLE public.jobs_raw ADD COLUMN IF NOT EXISTS processed BOOLEAN NOT NULL DEFAULT FALSE;
-- ALTER TABLE public.jobs_raw ADD COLUMN IF NOT EXISTS processed_at TIMESTAMP WITH TIME ZONE;

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_jobs_raw_url ON public.jobs_raw(url_publicacion);
CREATE INDEX IF NOT EXISTS idx_jobs_raw_processed ON public.jobs_raw(processed);
CREATE INDEX IF NOT EXISTS idx_jobs_clean_url ON public.jobs_clean(url_publicacion);
CREATE INDEX IF NOT EXISTS idx_jobs_url ON public.jobs(url_publicacion);
CREATE INDEX IF NOT EXISTS idx_jobs_embedding ON public.jobs USING ivfflat (embedding vector_cosine_ops);

-- Habilitar Row Level Security (RLS) si es necesario
-- ALTER TABLE public.jobs_raw ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.jobs_clean ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- Políticas de seguridad (ajusta según tus necesidades)
-- CREATE POLICY "Allow all operations" ON public.jobs_raw FOR ALL USING (true);
-- CREATE POLICY "Allow all operations" ON public.jobs_clean FOR ALL USING (true);
-- CREATE POLICY "Allow all operations" ON public.jobs FOR ALL USING (true);
