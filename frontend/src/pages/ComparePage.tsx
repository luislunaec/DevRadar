import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Download, TrendingUp } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { compararTecnologias, getHabilidadesPopulares, type ComparacionTecnologias } from '@/services/api';
import { exportComparacionToPdf } from '@/lib/exportComparePdf';

export default function ComparePage() {
  const [techA, setTechA] = useState('React');
  const [techB, setTechB] = useState('Angular');
  const [comparison, setComparison] = useState<ComparacionTecnologias | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchComparison = () => {
    setLoading(true);
    setError(null);
    compararTecnologias({ tecnologia_a: techA, tecnologia_b: techB })
      .then(setComparison)
      .catch((e) => setError(e instanceof Error ? e.message : 'Error al comparar'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchComparison();
  }, []);

  useEffect(() => {
    getHabilidadesPopulares(30).then(setSuggestions).catch(() => []);
  }, []);

  const a = comparison?.tecnologia_a;
  const b = comparison?.tecnologia_b;
  const trendData = comparison?.tendencia_historica?.map((t) => ({
    mes: t.mes,
    [techA]: t.valor_a,
    [techB]: t.valor_b,
  })) ?? [];

  return (
    <Layout showFooter={false}>
      <div className="container py-8">
        <div className="flex items-center gap-4 mb-8">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/dashboard">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Volver al Dashboard
            </Link>
          </Button>
          <h1 className="text-h2">DevRadar Ecuador</h1>
        </div>

        {/* Form: elegir tecnologías */}
        <div className="glass-card p-6 mb-6 flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[140px]">
            <label className="text-sm text-muted-foreground block mb-1">Tecnología A</label>
            <Input
              value={techA}
              onChange={(e) => setTechA(e.target.value)}
              placeholder="ej. React"
              className="bg-secondary"
            />
          </div>
          <div className="flex-1 min-w-[140px]">
            <label className="text-sm text-muted-foreground block mb-1">Tecnología B</label>
            <Input
              value={techB}
              onChange={(e) => setTechB(e.target.value)}
              placeholder="ej. Angular"
              className="bg-secondary"
            />
          </div>
          <Button onClick={fetchComparison} disabled={loading}>
            {loading ? 'Cargando...' : 'Comparar'}
          </Button>
          {suggestions.length > 0 && (
            <div className="w-full flex flex-wrap gap-2 mt-2">
              {suggestions.slice(0, 10).map((s) => (
                <Button
                  key={s}
                  variant="ghost"
                  size="sm"
                  onClick={() => { setTechA(s); fetchComparison(); }}
                >
                  {s}
                </Button>
              ))}
            </div>
          )}
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-destructive/10 text-destructive text-sm">{error}</div>
        )}

        {loading && !comparison ? (
          <div className="glass-card p-12 text-center text-muted-foreground">Cargando comparación...</div>
        ) : comparison && a && b ? (
          <>
            <div className="glass-card p-8 mb-6">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4">
                  <div className="p-4 rounded-xl bg-primary/10 text-primary">
                    <TrendingUp className="h-8 w-8" />
                  </div>
                  <div>
                    <h2 className="text-h1">{a.nombre}</h2>
                    <Badge variant="outline" className="text-primary border-primary">{a.tipo}</Badge>
                  </div>
                </div>
                <div className="flex items-center justify-center w-16 h-16 rounded-full border-2 border-border text-muted-foreground font-bold">VS</div>
                <div className="flex items-center gap-4 text-right">
                  <div>
                    <h2 className="text-h1">{b.nombre}</h2>
                    <Badge variant="outline" className="text-accent-purple border-accent-purple">{b.tipo}</Badge>
                  </div>
                  <div className="p-4 rounded-xl bg-accent-purple/10 text-accent-purple">
                    <TrendingUp className="h-8 w-8" />
                  </div>
                </div>
              </div>
            </div>

            <div className="glass-card p-6 mb-6">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 rounded-lg bg-secondary/50">
                  <p className="text-sm text-muted-foreground mb-1">{a.nombre}</p>
                  <p className="text-h1">${Math.round(a.salario_promedio).toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">/mes</p>
                </div>
                <div className="flex flex-col items-center justify-center">
                  <p className="text-caption text-muted-foreground mb-2">SALARIO PROMEDIO</p>
                  <div className="flex gap-4 text-sm">
                    <span className="text-success flex items-center gap-1">
                      <TrendingUp className="h-4 w-4" />
                      +{a.salario_variacion}% <span className="text-muted-foreground">vs año anterior</span>
                    </span>
                    <span className="text-success flex items-center gap-1">
                      +{b.salario_variacion}% <span className="text-muted-foreground">vs año anterior</span>
                    </span>
                  </div>
                </div>
                <div className="text-center p-4 rounded-lg bg-secondary/50">
                  <p className="text-sm text-muted-foreground mb-1">{b.nombre}</p>
                  <p className="text-h1">${Math.round(b.salario_promedio).toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">/mes</p>
                </div>
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-6 mb-6">
              <div className="glass-card p-6">
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-3xl font-bold text-success">{a.vacantes_activas}</p>
                    <p className="text-sm text-muted-foreground">Vacantes Activas</p>
                    <div className="h-2 bg-secondary rounded-full mt-2 overflow-hidden">
                      <div className="h-full bg-success" style={{ width: `${a.cuota_mercado}%` }} />
                    </div>
                  </div>
                  <div className="flex items-center justify-center">
                    <Badge variant="outline">DEMANDA (OFERTAS)</Badge>
                  </div>
                  <div className="text-right">
                    <p className="text-3xl font-bold text-primary">{b.vacantes_activas}</p>
                    <p className="text-sm text-muted-foreground">Vacantes Activas</p>
                    <div className="h-2 bg-secondary rounded-full mt-2 overflow-hidden">
                      <div className="h-full bg-primary ml-auto" style={{ width: `${b.cuota_mercado}%` }} />
                    </div>
                  </div>
                </div>
              </div>
              <div className="glass-card p-6">
                <div className="grid grid-cols-3 gap-4">
                  <div className="flex items-center gap-3">
                    <div className="relative w-16 h-16">
                      <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                        <circle cx="18" cy="18" r="16" fill="none" stroke="hsl(var(--secondary))" strokeWidth="3" />
                        <circle cx="18" cy="18" r="16" fill="none" stroke="hsl(var(--primary))" strokeWidth="3" strokeDasharray={`${a.cuota_mercado} 100`} />
                      </svg>
                      <span className="absolute inset-0 flex items-center justify-center text-sm font-bold">{a.cuota_mercado}%</span>
                    </div>
                    <div>
                      <p className="font-bold">{a.nombre}</p>
                      <p className="text-xs text-muted-foreground">Cuota de mercado</p>
                    </div>
                  </div>
                  <div className="flex items-center justify-center">
                    <Badge variant="outline">CUOTA DE MERCADO</Badge>
                  </div>
                  <div className="flex items-center gap-3 justify-end">
                    <div className="text-right">
                      <p className="font-bold">{b.nombre}</p>
                      <p className="text-xs text-muted-foreground">Cuota de mercado</p>
                    </div>
                    <div className="relative w-16 h-16">
                      <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                        <circle cx="18" cy="18" r="16" fill="none" stroke="hsl(var(--secondary))" strokeWidth="3" />
                        <circle cx="18" cy="18" r="16" fill="none" stroke="hsl(var(--accent-purple))" strokeWidth="3" strokeDasharray={`${b.cuota_mercado} 100`} />
                      </svg>
                      <span className="absolute inset-0 flex items-center justify-center text-sm font-bold">{b.cuota_mercado}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {trendData.length > 0 && (
              <div className="glass-card p-6 mb-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-h3">Tendencia Histórica Comparada</h3>
                    <p className="text-sm text-muted-foreground">Volumen de ofertas (datos del backend)</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-primary" />
                      <span className="text-sm">{techA}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-accent-purple" />
                      <span className="text-sm">{techB}</span>
                    </div>
                  </div>
                </div>
                <div className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="mes" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                      <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                      <Tooltip contentStyle={{ backgroundColor: 'hsl(220, 30%, 15%)', border: '1px solid hsl(220, 25%, 18%)', borderRadius: '8px' }} />
                      <Line type="monotone" dataKey={techA} stroke="hsl(217, 92%, 62%)" strokeWidth={2} dot={{ r: 4 }} />
                      <Line type="monotone" dataKey={techB} stroke="hsl(263, 70%, 66%)" strokeWidth={2} dot={{ r: 4 }} strokeDasharray="5 5" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {comparison?.conclusion && (
              <>
                {comparison.conclusion.veredicto_final && (
                  <div className="glass-card p-6 mb-6 border-l-4 border-primary bg-primary/5">
                    <h4 className="font-bold text-primary mb-2">Veredicto final</h4>
                    <p className="text-sm text-muted-foreground">{comparison.conclusion.veredicto_final}</p>
                  </div>
                )}
                <div className="grid md:grid-cols-3 gap-6 mb-6">
                  <div className="glass-card p-6 border-l-4 border-primary">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="h-5 w-5 text-primary" />
                      <h4 className="font-bold text-primary">Conclusión {a?.nombre}</h4>
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">{comparison.conclusion.resumen_a}</p>
                    {(comparison.conclusion.cosas_buenas_a?.length ?? 0) > 0 && (
                      <div className="mt-3 pt-3 border-t border-border">
                        <p className="text-xs font-medium text-primary mb-2">Cosas buenas</p>
                        <ul className="space-y-1 text-sm text-muted-foreground">
                          {comparison.conclusion.cosas_buenas_a?.map((item, i) => (
                            <li key={i} className="flex gap-2">
                              <span className="text-primary">•</span>
                              {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  <div className="glass-card p-6 border-l-4 border-warning">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="h-5 w-5 text-warning" />
                      <h4 className="font-bold text-warning">Veredicto Neutral</h4>
                    </div>
                    <p className="text-sm text-muted-foreground">{comparison.conclusion.resumen_neutral}</p>
                  </div>
                  <div className="glass-card p-6 border-l-4 border-accent-purple">
                    <div className="flex items-center gap-2 mb-3">
                      <TrendingUp className="h-5 w-5 text-accent-purple" />
                      <h4 className="font-bold text-accent-purple">Conclusión {b?.nombre}</h4>
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">{comparison.conclusion.resumen_b}</p>
                    {(comparison.conclusion.cosas_buenas_b?.length ?? 0) > 0 && (
                      <div className="mt-3 pt-3 border-t border-border">
                        <p className="text-xs font-medium text-accent-purple mb-2">Cosas buenas</p>
                        <ul className="space-y-1 text-sm text-muted-foreground">
                          {comparison.conclusion.cosas_buenas_b?.map((item, i) => (
                            <li key={i} className="flex gap-2">
                              <span className="text-accent-purple">•</span>
                              {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </>
            )}
            </>
          ) : null}

        <div className="flex justify-center">
          <Button
            variant="outline"
            size="lg"
            className="gap-2"
            disabled={!comparison}
            onClick={() => comparison && exportComparacionToPdf(techA, techB, comparison)}
          >
            <Download className="h-5 w-5" />
            Exportar Informe PDF
          </Button>
        </div>
      </div>
    </Layout>
  );
}
