import { useState } from 'react';
import { Diamond, Send, TrendingUp, Sparkles, Lightbulb, Smile } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ProgressBar } from '@/components/ProgressBar';
import { generarReporteIA, type ReporteIA } from '@/services/api';

const suggestedQueries = [
  'Salarios en Quito',
  'Remote vs On-site',
  'Seniority trends',
  'Top Frameworks',
];

export default function AIReportsPage() {
  const [query, setQuery] = useState('');
  const [report, setReport] = useState<ReporteIA | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await generarReporteIA({
        pregunta: query,
        region: 'Ecuador',
        incluir_graficos: true,
      });
      setReport(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error generando reporte');
    } finally {
      setLoading(false);
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
          {query && (
            <div className="flex justify-end">
              <div className="flex items-start gap-3">
                <div className="glass-card p-4 bg-primary text-primary-foreground max-w-md">
                  <p className="text-sm">{query}</p>
                </div>
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                  <span className="text-xs font-bold text-primary">Tú</span>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="p-4 rounded-lg bg-destructive/10 text-destructive text-sm">{error}</div>
          )}

          {loading && (
            <div className="flex gap-3">
              <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center shrink-0">
                <Sparkles className="h-5 w-5 text-primary-foreground animate-pulse" />
              </div>
              <p className="text-sm text-muted-foreground">Generando reporte...</p>
            </div>
          )}

          {report && !loading && (
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
                        Región: {report.region} • Período: {report.periodo}
                      </p>
                    </div>
                    <Badge className="bg-success/20 text-success border-success/30">
                      {report.actualizado}
                    </Badge>
                  </div>
                  <div className="mb-6">
                    <h4 className="text-caption text-error uppercase mb-3">RESUMEN EJECUTIVO</h4>
                    <ul className="space-y-2">
                      {(report.resumen_ejecutivo || []).map((item, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                          <TrendingUp className="h-4 w-4 text-success shrink-0 mt-0.5" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="mb-6">
                    <h4 className="text-caption text-error uppercase mb-4">TOP HERRAMIENTAS (DEMANDA %)</h4>
                    <div className="space-y-3">
                      {(report.top_herramientas || []).map((tool) => (
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
                  {report.tendencia_crecimiento && report.tendencia_crecimiento.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-caption text-error uppercase mb-3">TENDENCIA DE CRECIMIENTO ANUAL</h4>
                      <div className="h-24 bg-secondary/50 rounded-lg flex items-end justify-around gap-1 p-2">
                        {report.tendencia_crecimiento.map((t, i) => (
                          <div
                            key={i}
                            className="flex-1 bg-primary/30 rounded min-w-[8px]"
                            style={{ height: `${Math.min(100, (t.valor || 0) % 100)}%` }}
                          />
                        ))}
                      </div>
                    </div>
                  )}
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
