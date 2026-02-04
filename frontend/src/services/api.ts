// ===================================
// DevRadar Ecuador - API Service
// FastAPI Backend Endpoints
// ===================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Types based on Supabase table structure
export interface OfertaLaboral {
  id: string;
  plataforma: string;
  rol_busqueda: string;
  fecha_publicacion: string;
  oferta_laboral: string;
  locacion: string;
  descripcion: string;
  sueldo: string | null;
  compania: string;
  habilidades: string[];
  url_publicacion: string;
  created_at: string;
  seniority: 'junior' | 'semi-senior' | 'senior' | null;
}

export interface EstadisticasMercado {
  total_ofertas: number;
  ofertas_variacion_porcentaje: number;
  salario_promedio: number;
  salario_variacion_porcentaje: number;
  nivel_demanda: 'bajo' | 'medio' | 'alto';
  nuevas_vacantes_porcentaje: number;
}

export interface TecnologiaDemanda {
  nombre: string;
  porcentaje: number;
  total_ofertas: number;
}

export interface DistribucionSeniority {
  senior: number;
  semi_senior: number;
  junior: number;
}

export interface ComparacionTecnologias {
  tecnologia_a: {
    nombre: string;
    tipo: string;
    salario_promedio: number;
    salario_variacion: number;
    vacantes_activas: number;
    cuota_mercado: number;
    tendencia: 'dominante' | 'creciente' | 'estable' | 'decreciente';
  };
  tecnologia_b: {
    nombre: string;
    tipo: string;
    salario_promedio: number;
    salario_variacion: number;
    vacantes_activas: number;
    cuota_mercado: number;
    tendencia: 'dominante' | 'creciente' | 'estable' | 'decreciente';
  };
  tendencia_historica: {
    mes: string;
    valor_a: number;
    valor_b: number;
  }[];
  conclusion: {
    ganador: 'a' | 'b' | 'neutral';
    resumen_a: string;
    resumen_b: string;
    resumen_neutral: string;
    cosas_buenas_a?: string[];
    cosas_buenas_b?: string[];
    veredicto_final?: string;
  };
}

export interface AnalisisCV {
  compatibilidad_porcentaje: number;
  nivel_seniority: 'junior' | 'semi-senior' | 'senior';
  resumen: string;
  habilidades_detectadas: string[];
  habilidades_faltantes: string[];
  sugerencias: {
    titulo: string;
    descripcion: string;
  }[];
}

export interface ReporteIA {
  region: string;
  periodo: string;
  actualizado: string;
  resumen_ejecutivo: string[];
  top_herramientas: {
    nombre: string;
    porcentaje: number;
  }[];
  tendencia_crecimiento: {
    mes: string;
    valor: number;
  }[];
}

export interface ChatMensaje {
  mensaje: string;
  session_id: string;
}

export interface ChatRespuesta {
  respuesta: string;
  ofertas_encontradas: number;
  rechazada: boolean;
}

export interface FiltrosOfertas {
  rol?: string;
  locacion?: string;
  seniority?: string;
  plataforma?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
  salario_min?: number;
  salario_max?: number;
  habilidades?: string[];
  page?: number;
  limit?: number;
}

// ===================================
// ENDPOINTS PARA FASTAPI
// ===================================

/**
 * GET /api/ofertas
 * Obtener lista de ofertas laborales con filtros
 * 
 * Query params:
 * - rol: string (opcional) - Filtrar por rol de búsqueda
 * - locacion: string (opcional) - Ciudad/ubicación
 * - seniority: 'junior' | 'semi-senior' | 'senior' (opcional)
 * - plataforma: string (opcional) - Fuente de la oferta
 * - fecha_desde: string (ISO date, opcional)
 * - fecha_hasta: string (ISO date, opcional)
 * - salario_min: number (opcional)
 * - salario_max: number (opcional)
 * - habilidades: string[] (opcional) - Lista de skills
 * - page: number (default: 1)
 * - limit: number (default: 20)
 */
export async function getOfertas(filtros: FiltrosOfertas = {}): Promise<{
  data: OfertaLaboral[];
  total: number;
  page: number;
  total_pages: number;
}> {
  const params = new URLSearchParams();

  Object.entries(filtros).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        value.forEach(v => params.append(key, v));
      } else {
        params.append(key, String(value));
      }
    }
  });

  const response = await fetch(`${API_BASE_URL}/ofertas?${params}`);
  if (!response.ok) throw new Error('Error fetching ofertas');
  return response.json();
}

/**
 * GET /api/ofertas/{id}
 * Obtener detalle de una oferta específica
 */
export async function getOfertaById(id: string): Promise<OfertaLaboral> {
  const response = await fetch(`${API_BASE_URL}/ofertas/${id}`);
  if (!response.ok) throw new Error('Error fetching oferta');
  return response.json();
}

/**
 * GET /api/estadisticas/mercado
 * Obtener estadísticas generales del mercado
 * 
 * Query params:
 * - rol: string (opcional) - Filtrar por rol específico
 * - fecha_desde: string (ISO date, opcional)
 * - fecha_hasta: string (ISO date, opcional)
 */
export async function getEstadisticasMercado(params?: {
  rol?: string;
  fecha_desde?: string;
  fecha_hasta?: string;
}): Promise<EstadisticasMercado> {
  const searchParams = new URLSearchParams();
  if (params?.rol) searchParams.append('rol', params.rol);
  if (params?.fecha_desde) searchParams.append('fecha_desde', params.fecha_desde);
  if (params?.fecha_hasta) searchParams.append('fecha_hasta', params.fecha_hasta);

  const response = await fetch(`${API_BASE_URL}/estadisticas/mercado?${searchParams}`);
  if (!response.ok) throw new Error('Error fetching estadísticas');
  return response.json();
}

/**
 * GET /api/estadisticas/tecnologias
 * Obtener top tecnologías más demandadas
 * 
 * Query params:
 * - limit: number (default: 10) - Cantidad de tecnologías a retornar
 * - rol: string (opcional) - Filtrar por rol
 */
export async function getTecnologiasDemandadas(params?: {
  limit?: number;
  rol?: string;
}): Promise<TecnologiaDemanda[]> {
  const searchParams = new URLSearchParams();
  if (params?.limit) searchParams.append('limit', String(params.limit));
  if (params?.rol) searchParams.append('rol', params.rol);

  const response = await fetch(`${API_BASE_URL}/estadisticas/tecnologias?${searchParams}`);
  if (!response.ok) throw new Error('Error fetching tecnologías');
  return response.json();
}

/**
 * GET /api/estadisticas/seniority
 * Obtener distribución por nivel de experiencia
 * 
 * Query params:
 * - rol: string (opcional) - Filtrar por rol
 */
export async function getDistribucionSeniority(rol?: string): Promise<DistribucionSeniority> {
  const params = rol ? `?rol=${encodeURIComponent(rol)}` : '';
  const response = await fetch(`${API_BASE_URL}/estadisticas/seniority${params}`);
  if (!response.ok) throw new Error('Error fetching seniority');
  return response.json();
}

/**
 * POST /api/comparar-tecnologias
 * Comparar dos tecnologías
 * 
 * Body:
 * {
 *   tecnologia_a: string,
 *   tecnologia_b: string,
 *   periodo_meses?: number (default: 12)
 * }
 */
export async function compararTecnologias(data: {
  tecnologia_a: string;
  tecnologia_b: string;
  periodo_meses?: number;
}): Promise<ComparacionTecnologias> {
  const response = await fetch(`${API_BASE_URL}/comparar-tecnologias`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Error comparando tecnologías');
  return response.json();
}

/**
 * POST /api/analizar-cv
 * Analizar CV y comparar con mercado
 * 
 * Body: FormData
 * - archivo: File (PDF o DOCX, max 10MB)
 * - rol_objetivo?: string (opcional)
 */
export async function analizarCV(archivo: File, rolObjetivo?: string): Promise<AnalisisCV> {
  const formData = new FormData();
  formData.append('archivo', archivo);
  if (rolObjetivo) formData.append('rol_objetivo', rolObjetivo);

  const response = await fetch(`${API_BASE_URL}/analizar-cv`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Error analizando CV');
  return response.json();
}

/**
 * POST /api/generar-reporte
 * Generar reporte de mercado con IA
 * 
 * Body:
 * {
 *   pregunta: string,
 *   region?: string,
 *   incluir_graficos?: boolean
 * }
 */
export async function generarReporteIA(data: {
  pregunta: string;
  region?: string;
  incluir_graficos?: boolean;
}): Promise<ReporteIA> {
  const response = await fetch(`${API_BASE_URL}/generar-reporte`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Error generando reporte');
  return response.json();
}

/**
 * POST /api/chat
 * Enviar mensaje al chatbot con IA
 * 
 * Body:
 * {
 *   mensaje: string,
 *   session_id: string
 * }
 */
export async function enviarMensajeChat(data: ChatMensaje): Promise<ChatRespuesta> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Error en el chat');
  return response.json();
}

/**
 * GET /api/roles-disponibles
 * Obtener lista de roles disponibles para búsqueda
 */
export async function getRolesDisponibles(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/roles-disponibles`);
  if (!response.ok) throw new Error('Error fetching roles');
  return response.json();
}

/**
 * GET /api/ubicaciones
 * Obtener lista de ubicaciones/ciudades disponibles
 */
export async function getUbicaciones(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/ubicaciones`);
  if (!response.ok) throw new Error('Error fetching ubicaciones');
  return response.json();
}

/**
 * GET /api/habilidades-populares
 * Obtener lista de habilidades más populares
 * 
 * Query params:
 * - limit: number (default: 50)
 */
export async function getHabilidadesPopulares(limit?: number): Promise<string[]> {
  const params = limit ? `?limit=${limit}` : '';
  const response = await fetch(`${API_BASE_URL}/habilidades-populares${params}`);
  if (!response.ok) throw new Error('Error fetching habilidades');
  return response.json();
}
