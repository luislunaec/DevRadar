import { useState, useCallback } from 'react';
import { Upload, FileText, AlertTriangle, Lightbulb } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { analizarCV, type AnalisisCV } from '@/services/api';

export default function CVAnalysisPage() {
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalisisCV | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === 'application/pdf' || droppedFile.name.endsWith('.docx'))) {
      setFile(droppedFile);
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setAnalysis(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const result = await analizarCV(file);
      setAnalysis(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error analizando CV');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="container py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-h1 mb-2">Análisis de CV con IA</h1>
          <p className="text-muted-foreground">
            Optimiza tu perfil profesional basándote en la demanda real del mercado IT en Ecuador.
          </p>
        </div>

        {/* Upload Area */}
        <div className="max-w-3xl mx-auto mb-8">
          <div
            className={`glass-card p-12 border-2 border-dashed transition-colors ${
              isDragging ? 'border-primary bg-primary/5' : 'border-border'
            }`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <div className="text-center">
              <div className="inline-flex p-4 rounded-full bg-primary/10 text-primary mb-4">
                <Upload className="h-8 w-8" />
              </div>
              <h3 className="text-h3 mb-2">Sube tu CV para comenzar</h3>
              <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
                Arrastra y suelta tu archivo PDF o Word aquí. El sistema identificará tus fortalezas y brechas frente al mercado de Quito, Guayaquil y Cuenca.
              </p>
              <div className="flex flex-wrap gap-3 items-center justify-center">
                <label>
                  <Button size="lg" asChild>
                    <span>
                      <FileText className="h-5 w-5 mr-2" />
                      Seleccionar Archivo
                    </span>
                  </Button>
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.docx"
                    onChange={handleFileChange}
                  />
                </label>
                {file && (
                  <Button size="lg" onClick={handleAnalyze} disabled={loading}>
                    {loading ? 'Analizando...' : 'Analizar CV'}
                  </Button>
                )}
              </div>
              <p className="text-xs text-muted-foreground mt-4">
                Máximo 10MB (PDF, DOCX)
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="max-w-3xl mx-auto mb-6 p-4 rounded-lg bg-destructive/10 text-destructive text-sm">
            {error}
          </div>
        )}

        {analysis && (
          <div className="grid lg:grid-cols-2 gap-6 max-w-5xl mx-auto">
            <div className="glass-card p-6">
              <h3 className="text-caption text-muted-foreground uppercase mb-4">
                COMPATIBILIDAD CON EL MERCADO
              </h3>
              <div className="flex items-center gap-6">
                <div className="relative w-32 h-32">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                    <circle cx="18" cy="18" r="15.5" fill="none" stroke="hsl(var(--secondary))" strokeWidth="3" />
                    <circle
                      cx="18" cy="18" r="15.5"
                      fill="none"
                      stroke="hsl(var(--primary))"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeDasharray={`${analysis.compatibilidad_porcentaje} 100`}
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-bold">{analysis.compatibilidad_porcentaje}%</span>
                    <span className="text-xs text-muted-foreground">Nivel {analysis.nivel_seniority}</span>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">{analysis.resumen}</p>
              </div>
            </div>

            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-h3">Habilidades Detectadas</h3>
                <Badge className="bg-success/20 text-success border-success/30">
                  {analysis.habilidades_detectadas?.length ?? 0} Encontradas
                </Badge>
              </div>
              <div className="flex flex-wrap gap-2 mb-6">
                {(analysis.habilidades_detectadas || []).map((skill) => (
                  <Badge key={skill} variant="secondary" className="bg-primary/10 text-primary border-primary/30">
                    {skill}
                  </Badge>
                ))}
              </div>
              <div className="border-t border-border pt-4">
                <div className="flex items-center gap-2 mb-3">
                  <AlertTriangle className="h-4 w-4 text-warning" />
                  <span className="text-sm font-medium">Habilidades Faltantes (Skill Gaps)</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {(analysis.habilidades_faltantes || []).map((skill) => (
                    <Badge key={skill} variant="outline" className="border-warning/50 text-warning">
                      {skill}
                    </Badge>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground mt-3">
                  Estas habilidades son demandadas en el mercado actual.
                </p>
              </div>
            </div>

            <div className="glass-card p-6 lg:col-span-2">
              <div className="flex items-center gap-2 mb-6">
                <Lightbulb className="h-5 w-5 text-warning" />
                <h3 className="text-h3">Sugerencias de Mejora</h3>
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                {(analysis.sugerencias || []).map((suggestion, index) => (
                  <div key={index} className="flex gap-3">
                    <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-xs font-bold shrink-0">
                      {index + 1}
                    </div>
                    <div>
                      <h4 className="font-medium mb-1">{suggestion.titulo}</h4>
                      <p className="text-sm text-muted-foreground">{suggestion.descripcion}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-border mt-12">
        <div className="container py-6">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              © 2024 DevRadar Ecuador - Impulsado por IA
            </p>
            <div className="flex gap-6">
              <a href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                Privacidad
              </a>
              <a href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                Términos de Uso
              </a>
              <a href="#" className="text-sm text-muted-foreground hover:text-primary transition-colors">
                Feedback
              </a>
            </div>
          </div>
        </div>
      </footer>
    </Layout>
  );
}
