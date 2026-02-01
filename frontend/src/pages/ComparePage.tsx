import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Download, TrendingUp, TrendingDown } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

// Mock data - will be replaced by API calls
const mockComparison = {
  tecnologia_a: {
    nombre: 'React',
    tipo: 'Frontend Library',
    salario: 2500,
    salario_variacion: 12,
    vacantes: 150,
    cuota_mercado: 65,
  },
  tecnologia_b: {
    nombre: 'Angular',
    tipo: 'Frontend Framework',
    salario: 2300,
    salario_variacion: 5,
    vacantes: 85,
    cuota_mercado: 35,
  },
};

const mockTrendData = [
  { mes: 'ENE', React: 120, Angular: 80 },
  { mes: 'FEB', React: 125, Angular: 82 },
  { mes: 'MAR', React: 130, Angular: 78 },
  { mes: 'ABR', React: 135, Angular: 85 },
  { mes: 'MAY', React: 140, Angular: 83 },
  { mes: 'JUN', React: 138, Angular: 80 },
  { mes: 'JUL', React: 145, Angular: 82 },
  { mes: 'AGO', React: 150, Angular: 84 },
  { mes: 'SEP', React: 155, Angular: 85 },
  { mes: 'OCT', React: 160, Angular: 86 },
  { mes: 'NOV', React: 165, Angular: 87 },
  { mes: 'DIC', React: 170, Angular: 88 },
];

export default function ComparePage() {
  return (
    <Layout showFooter={false}>
      <div className="container py-8">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/dashboard">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Volver al Dashboard
            </Link>
          </Button>
          <h1 className="text-h2">DevRadar Ecuador</h1>
        </div>

        {/* Tech Comparison Header */}
        <div className="glass-card p-8 mb-6">
          <div className="flex items-center justify-between">
            {/* Tech A */}
            <div className="flex items-center gap-4">
              <div className="p-4 rounded-xl bg-primary/10 text-primary">
                <TrendingUp className="h-8 w-8" />
              </div>
              <div>
                <h2 className="text-h1">{mockComparison.tecnologia_a.nombre}</h2>
                <Badge variant="outline" className="text-primary border-primary">
                  {mockComparison.tecnologia_a.tipo}
                </Badge>
              </div>
            </div>

            {/* VS */}
            <div className="flex items-center justify-center w-16 h-16 rounded-full border-2 border-border text-muted-foreground font-bold">
              VS
            </div>

            {/* Tech B */}
            <div className="flex items-center gap-4 text-right">
              <div>
                <h2 className="text-h1">{mockComparison.tecnologia_b.nombre}</h2>
                <Badge variant="outline" className="text-accent-purple border-accent-purple">
                  {mockComparison.tecnologia_b.tipo}
                </Badge>
              </div>
              <div className="p-4 rounded-xl bg-accent-purple/10 text-accent-purple">
                <TrendingUp className="h-8 w-8" />
              </div>
            </div>
          </div>
        </div>

        {/* Salary Comparison */}
        <div className="glass-card p-6 mb-6">
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 rounded-lg bg-secondary/50">
              <p className="text-sm text-muted-foreground mb-1">{mockComparison.tecnologia_a.nombre}</p>
              <p className="text-h1">${mockComparison.tecnologia_a.salario.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">/mes</p>
            </div>
            
            <div className="flex flex-col items-center justify-center">
              <p className="text-caption text-muted-foreground mb-2">SALARIO PROMEDIO</p>
              <div className="flex gap-4 text-sm">
                <span className="text-success flex items-center gap-1">
                  <TrendingUp className="h-4 w-4" />
                  +{mockComparison.tecnologia_a.salario_variacion}%
                  <span className="text-muted-foreground">vs año anterior</span>
                </span>
                <span className="text-success flex items-center gap-1">
                  +{mockComparison.tecnologia_b.salario_variacion}%
                  <span className="text-muted-foreground">vs año anterior</span>
                </span>
              </div>
            </div>
            
            <div className="text-center p-4 rounded-lg bg-secondary/50">
              <p className="text-sm text-muted-foreground mb-1">{mockComparison.tecnologia_b.nombre}</p>
              <p className="text-h1">${mockComparison.tecnologia_b.salario.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">/mes</p>
            </div>
          </div>
        </div>

        {/* Demand & Market Share */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Demand */}
          <div className="glass-card p-6">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-3xl font-bold text-success">{mockComparison.tecnologia_a.vacantes}</p>
                <p className="text-sm text-muted-foreground">Vacantes Activas</p>
                <div className="h-2 bg-secondary rounded-full mt-2 overflow-hidden">
                  <div className="h-full bg-success" style={{ width: '65%' }} />
                </div>
                <p className="text-xs text-success mt-1">Alta Demanda</p>
              </div>
              
              <div className="flex items-center justify-center">
                <Badge variant="outline">DEMANDA (OFERTAS)</Badge>
              </div>
              
              <div className="text-right">
                <p className="text-3xl font-bold text-primary">{mockComparison.tecnologia_b.vacantes}</p>
                <p className="text-sm text-muted-foreground">Vacantes Activas</p>
                <div className="h-2 bg-secondary rounded-full mt-2 overflow-hidden">
                  <div className="h-full bg-primary ml-auto" style={{ width: '35%' }} />
                </div>
                <p className="text-xs text-muted-foreground mt-1">Demanda Media</p>
              </div>
            </div>
          </div>

          {/* Market Share */}
          <div className="glass-card p-6">
            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center gap-3">
                <div className="relative w-16 h-16">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="16" fill="none" stroke="hsl(var(--secondary))" strokeWidth="3" />
                    <circle
                      cx="18" cy="18" r="16" fill="none"
                      stroke="hsl(var(--primary))"
                      strokeWidth="3"
                      strokeDasharray={`${mockComparison.tecnologia_a.cuota_mercado} 100`}
                    />
                  </svg>
                  <span className="absolute inset-0 flex items-center justify-center text-sm font-bold">
                    {mockComparison.tecnologia_a.cuota_mercado}%
                  </span>
                </div>
                <div>
                  <p className="font-bold">Dominante</p>
                  <p className="text-xs text-muted-foreground">Presencia en Startups y Empresas Tech modernas</p>
                </div>
              </div>
              
              <div className="flex items-center justify-center">
                <Badge variant="outline">CUOTA DE MERCADO</Badge>
              </div>
              
              <div className="flex items-center gap-3 justify-end">
                <div className="text-right">
                  <p className="font-bold">Corporativo</p>
                  <p className="text-xs text-muted-foreground">Fuerte presencia en Banca y Enterprise Legacy</p>
                </div>
                <div className="relative w-16 h-16">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="16" fill="none" stroke="hsl(var(--secondary))" strokeWidth="3" />
                    <circle
                      cx="18" cy="18" r="16" fill="none"
                      stroke="hsl(var(--accent-purple))"
                      strokeWidth="3"
                      strokeDasharray={`${mockComparison.tecnologia_b.cuota_mercado} 100`}
                    />
                  </svg>
                  <span className="absolute inset-0 flex items-center justify-center text-sm font-bold">
                    {mockComparison.tecnologia_b.cuota_mercado}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Trend Chart */}
        <div className="glass-card p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-h3">Tendencia Histórica Comparada</h3>
              <p className="text-sm text-muted-foreground">Volumen de ofertas publicadas en los últimos 12 meses</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-primary" />
                <span className="text-sm">React</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-accent-purple" />
                <span className="text-sm">Angular</span>
              </div>
            </div>
          </div>
          
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockTrendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="mes" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(220, 30%, 15%)',
                    border: '1px solid hsl(220, 25%, 18%)',
                    borderRadius: '8px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="React"
                  stroke="hsl(217, 92%, 62%)"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="Angular"
                  stroke="hsl(263, 70%, 66%)"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  strokeDasharray="5 5"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Conclusions */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="glass-card p-6 border-l-4 border-primary">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="h-5 w-5 text-primary" />
              <h4 className="font-bold text-primary">Conclusión React</h4>
            </div>
            <p className="text-sm text-muted-foreground">
              Ideal para quienes buscan mayor volumen de oportunidades y trabajo en proyectos innovadores. El salario techo es más alto en roles senior remotos.
            </p>
          </div>
          
          <div className="glass-card p-6 border-l-4 border-warning">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="h-5 w-5 text-warning" />
              <h4 className="font-bold text-warning">Veredicto Neutral</h4>
            </div>
            <p className="text-sm text-muted-foreground">
              Ambas tecnologías tienen una salud de mercado excelente. La elección depende más del tipo de industria (Startup vs Banca) que del riesgo de obsolescencia.
            </p>
          </div>
          
          <div className="glass-card p-6 border-l-4 border-accent-purple">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="h-5 w-5 text-accent-purple" />
              <h4 className="font-bold text-accent-purple">Conclusión Angular</h4>
            </div>
            <p className="text-sm text-muted-foreground">
              Ofrece mayor estabilidad laboral a largo plazo en grandes corporaciones ecuatorianas. Menor competencia por vacante comparado con React.
            </p>
          </div>
        </div>

        {/* Export Button */}
        <div className="flex justify-center">
          <Button variant="outline" size="lg" className="gap-2">
            <Download className="h-5 w-5" />
            Exportar Informe PDF
          </Button>
        </div>
      </div>
    </Layout>
  );
}
