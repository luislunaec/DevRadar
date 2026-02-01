import { useState } from 'react';
import { Diamond, Send, TrendingUp, Sparkles, Lightbulb, Smile } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ProgressBar';

const suggestedQueries = [
  'Salarios en Quito',
  'Remote vs On-site',
  'Seniority trends',
  'Top Frameworks',
];

// Mock AI response
const mockReport = {
  region: 'Guayaquil',
  periodo: 'Q1-Q4 2024',
  actualizado: 'ACTUALIZADO HOY',
  resumen: [
    'Incremento del 15% en la demanda de perfiles Fullstack con dominio de ecosistemas Cloud (AWS/Azure).',
    'El rango salarial promedio para perfiles Senior aumentó a $3,200 - $4,500 netos en el sector bancario de Guayaquil.',
    'El 65% de las vacantes en la ciudad mantienen un formato híbrido (2 días presenciales).',
  ],
  top_herramientas: [
    { nombre: 'React / Next.js', porcentaje: 88 },
    { nombre: 'Node.js / Express', porcentaje: 72 },
    { nombre: 'Python (Data Science)', porcentaje: 64 },
    { nombre: 'Java (Spring Boot)', porcentaje: 55 },
  ],
};

export default function AIReportsPage() {
  const [query, setQuery] = useState('');
  const [showReport, setShowReport] = useState(true); // Show mock by default for demo

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setShowReport(true);
    }
  };

  return (
    <Layout>
      <div className="container py-8">
        {/* Header */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <Diamond className="h-6 w-6 text-primary" />
          <span className="text-h3">DevRadar Ecuador</span>
        </div>

        {/* Title */}
        <div className="text-center mb-12">
          <h1 className="text-h1 mb-4">Generador de Reportes con IA</h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Analiza el mercado laboral IT en Ecuador con datos en tiempo real y visualizaciones avanzadas.
          </p>
        </div>

        {/* Chat Area */}
        <div className="max-w-4xl mx-auto space-y-6 mb-8">
          {/* User Message Example */}
          <div className="flex justify-end">
            <div className="flex items-start gap-3">
              <div className="glass-card p-4 bg-primary text-primary-foreground max-w-md">
                <p className="text-sm">¿Cuáles son las herramientas más usadas en Guayaquil para 2024?</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                <span className="text-xs font-bold text-primary">Tú</span>
              </div>
            </div>
          </div>

          {/* AI Response */}
          {showReport && (
            <div className="flex gap-3">
              <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center shrink-0">
                <Sparkles className="h-5 w-5 text-primary-foreground" />
              </div>
              <div className="flex-1 space-y-4">
                <p className="text-sm text-muted-foreground">DevRadar AI</p>
                
                <div className="glass-card p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-h3">Reporte Dinámico de Mercado</h3>
                      <p className="text-sm text-muted-foreground">
                        Región: {mockReport.region} • Período: {mockReport.periodo}
                      </p>
                    </div>
                    <Badge className="bg-success/20 text-success border-success/30">
                      {mockReport.actualizado}
                    </Badge>
                  </div>

                  {/* Executive Summary */}
                  <div className="mb-6">
                    <h4 className="text-caption text-error uppercase mb-3">RESUMEN EJECUTIVO</h4>
                    <ul className="space-y-2">
                      {mockReport.resumen.map((item, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                          <TrendingUp className="h-4 w-4 text-success shrink-0 mt-0.5" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Top Tools */}
                  <div className="mb-6">
                    <h4 className="text-caption text-error uppercase mb-4">TOP HERRAMIENTAS (DEMANDA %)</h4>
                    <div className="space-y-3">
                      {mockReport.top_herramientas.map((tool) => (
                        <ProgressBar
                          key={tool.nombre}
                          label={tool.nombre}
                          value={tool.porcentaje}
                          variant="primary"
                          size="sm"
                        />
                      ))}
                    </div>
                  </div>

                  {/* Growth Trend Placeholder */}
                  <div className="mb-4">
                    <h4 className="text-caption text-error uppercase mb-3">TENDENCIA DE CRECIMIENTO ANUAL</h4>
                    <div className="h-24 bg-secondary/50 rounded-lg flex items-end justify-end p-4">
                      <div className="w-32 h-16 bg-primary/30 rounded" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Suggested Queries */}
        <div className="max-w-4xl mx-auto mb-4">
          <div className="flex flex-wrap gap-2 justify-center">
            {suggestedQueries.map((suggestion) => (
              <Button
                key={suggestion}
                variant="outline"
                size="sm"
                onClick={() => setQuery(suggestion)}
                className="rounded-full"
              >
                {suggestion}
              </Button>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="glass-card p-4">
            <div className="flex items-center gap-3 mb-3">
              <Input
                type="text"
                placeholder="Ej: ¿Cuáles son las herramientas más usadas en Guayaquil para 2024?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="flex-1 bg-transparent border-0 focus-visible:ring-0 text-base"
              />
              <Button type="submit" size="lg" className="gap-2">
                Generar Reporte
                <Sparkles className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center gap-4 px-2">
              <button type="button" className="text-muted-foreground hover:text-foreground transition-colors">
                <Lightbulb className="h-5 w-5" />
              </button>
              <button type="button" className="text-muted-foreground hover:text-foreground transition-colors">
                <Send className="h-5 w-5" />
              </button>
              <button type="button" className="text-muted-foreground hover:text-foreground transition-colors">
                <Smile className="h-5 w-5" />
              </button>
            </div>
          </form>
          
          <p className="text-center text-xs text-muted-foreground mt-3">
            IA ENTRENADA CON DATOS DEL MERCADO IT ECUATORIANO 2024
          </p>
        </div>
      </div>
    </Layout>
  );
}
