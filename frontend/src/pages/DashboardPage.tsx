import { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Calendar, BarChart3, FileText, Sparkles, ArrowRight, Home } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { StatCard } from '@/components/StatCard';
import { ProgressBar } from '@/components/ProgressBar';
import { Button } from '@/components/ui/button';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

// Mock data - will be replaced by API calls
const mockStats = {
  total_ofertas: 1240,
  ofertas_variacion: 12,
  salario_promedio: 2500,
  salario_variacion: 5,
  nivel_demanda: 'Alto',
  nuevas_vacantes: 8,
};

const mockTecnologias = [
  { nombre: 'Node.js', porcentaje: 82 },
  { nombre: 'Python (Django/Flask)', porcentaje: 68 },
  { nombre: 'Java Spring Boot', porcentaje: 54 },
  { nombre: 'AWS Services', porcentaje: 45 },
  { nombre: 'Docker / Kubernetes', porcentaje: 38 },
];

const mockSeniority = [
  { name: 'Senior', value: 45, color: 'hsl(217, 92%, 62%)' },
  { name: 'Semi-Senior', value: 30, color: 'hsl(263, 70%, 66%)' },
  { name: 'Junior', value: 25, color: 'hsl(168, 76%, 40%)' },
];

export default function DashboardPage() {
  const [searchParams] = useSearchParams();
  const rol = searchParams.get('rol') || 'Backend Developer';
  const [dateRange, setDateRange] = useState('Oct 2023');

  return (
    <Layout showFooter={false}>
      <div className="flex min-h-[calc(100vh-4rem)]">
        {/* Main Content */}
        <div className="flex-1 p-6 lg:p-8">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <Link to="/" className="hover:text-primary">Resultados</Link>
            <span>/</span>
            <span className="text-foreground">{rol}</span>
          </div>

          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-h1">Análisis de Mercado</h1>
            <div className="flex items-center gap-4">
              <span className="text-sm text-success">Datos: {dateRange}</span>
              <Button variant="outline" size="sm" className="gap-2">
                <Calendar className="h-4 w-4" />
                Filtrar fecha
              </Button>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <StatCard
              label="Ofertas Analizadas"
              value={mockStats.total_ofertas.toLocaleString()}
              change={{ value: mockStats.ofertas_variacion, label: 'vs. mes anterior' }}
              icon={<BarChart3 className="h-5 w-5" />}
              variant="primary"
            />
            <StatCard
              label="Salario Promedio"
              value={`$${mockStats.salario_promedio.toLocaleString()}`}
              suffix="/mo"
              change={{ value: mockStats.salario_variacion, label: 'vs. mes anterior' }}
              icon={<FileText className="h-5 w-5" />}
              variant="success"
            />
            <StatCard
              label="Nivel de Demanda"
              value={mockStats.nivel_demanda}
              change={{ value: mockStats.nuevas_vacantes, label: 'nuevas vacantes' }}
              icon={<Sparkles className="h-5 w-5" />}
            />
          </div>

          {/* Charts Row */}
          <div className="grid lg:grid-cols-2 gap-6 mb-8">
            {/* Technologies */}
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-h3">Tecnologías Más Demandadas</h2>
                <Link to="#" className="text-sm text-primary hover:underline">
                  Ver todas
                </Link>
              </div>
              <div className="space-y-4">
                {mockTecnologias.map((tech) => (
                  <ProgressBar
                    key={tech.nombre}
                    label={tech.nombre}
                    value={tech.porcentaje}
                    variant="gradient"
                  />
                ))}
              </div>
            </div>

            {/* Seniority Distribution */}
            <div className="glass-card p-6">
              <h2 className="text-h3 mb-6">Nivel de Experiencia</h2>
              <div className="flex items-center gap-8">
                <div className="relative w-48 h-48">
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie
                        data={mockSeniority}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={2}
                        dataKey="value"
                      >
                        {mockSeniority.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'hsl(220, 30%, 15%)',
                          border: '1px solid hsl(220, 25%, 18%)',
                          borderRadius: '8px',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-bold">45%</span>
                    <span className="text-sm text-muted-foreground">Senior</span>
                  </div>
                </div>
                <div className="space-y-3">
                  {mockSeniority.map((item) => (
                    <div key={item.name} className="flex items-center gap-3">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-sm">{item.name}</span>
                      <span className="text-sm font-bold ml-auto">{item.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* AI Banner */}
          <div className="glass-card p-6 bg-gradient-to-r from-primary/10 to-accent-purple/10 border-primary/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-primary/20 text-primary">
                  <Sparkles className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-h3 text-primary">Análisis Inteligente Disponible</h3>
                  <p className="text-sm text-muted-foreground">
                    Nuestra IA ha detectado oportunidades salariales para este rol basadas en tu perfil actual. Descubre cómo aumentar tu competitividad.
                  </p>
                </div>
              </div>
              <div className="flex gap-3">
                <Button variant="outline" asChild>
                  <Link to="/compare">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Comparar Tecnologías
                  </Link>
                </Button>
                <Button asChild>
                  <Link to="/ai-reports">
                    <Sparkles className="h-4 w-4 mr-2" />
                    Ver Recomendación IA
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <aside className="hidden xl:block w-64 border-l border-border p-6 bg-sidebar">
          <div className="space-y-1 mb-8">
            <span className="text-h3">DevRadar</span>
            <p className="text-xs text-muted-foreground">Ecuador Edition</p>
          </div>

          <nav className="space-y-2">
            <Link
              to="/"
              className="flex items-center gap-3 px-4 py-3 rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
            >
              <Home className="h-5 w-5" />
              Inicio
            </Link>
            <Link
              to="/dashboard"
              className="flex items-center gap-3 px-4 py-3 rounded-lg bg-primary/10 text-primary"
            >
              <BarChart3 className="h-5 w-5" />
              Resultados
            </Link>
            <Link
              to="/cv-analysis"
              className="flex items-center gap-3 px-4 py-3 rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
            >
              <FileText className="h-5 w-5" />
              Análisis de CV
            </Link>
          </nav>
        </aside>
      </div>
    </Layout>
  );
}
