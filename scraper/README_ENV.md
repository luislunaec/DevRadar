# 🔐 Configuración de Credenciales

## Archivo .env

Crea un archivo `.env` en la raíz del proyecto con las siguientes credenciales:

```env
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key-aqui

# Google AI (Gemini)
GOOGLE_API_KEY=tu-google-api-key-aqui
```

## 📋 Cómo obtener las credenciales

### 1. Supabase

1. Ve a [https://supabase.com](https://supabase.com) e inicia sesión
2. Selecciona tu proyecto (o crea uno nuevo)
3. Ve a **Settings** → **API**
4. Copia:
   - **Project URL** → `SUPABASE_URL`
   - **service_role key** (secret) → `SUPABASE_KEY`
   - ⚠️ **IMPORTANTE**: Usa la `service_role` key, no la `anon` key, para tener permisos completos

### 2. Google AI (Gemini)

1. Ve a [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en **Create API Key**
4. Copia la API key generada → `GOOGLE_API_KEY`

## ⚠️ Seguridad

- **NUNCA** subas el archivo `.env` a Git
- El archivo `.env` ya está en `.gitignore`
- Usa `.env.example` como plantilla (sin valores reales)

## ✅ Verificación

Una vez configurado, puedes verificar que funciona ejecutando:

```bash
cd scraper
python main.py
```

O para ejecutar un scraper individual:

```bash
cd scraper
python scrapers/scraper_computrabajos.py
```

Si las credenciales son correctas, el flujo se ejecutará correctamente.
