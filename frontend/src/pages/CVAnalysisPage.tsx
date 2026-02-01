import { useState, useCallback } from 'react';
import { Upload, FileText, AlertTriangle, Check, Lightbulb } from 'lucide-react';
import { Layout } from '@/components/Layout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

// Mock analysis data
const mockAnalysis = {
  compatibilidad: 75,
  seniority: 'Senior',
  habilidades_detectadas: [
    'React.js', 'Node.js', 'TypeScript', 'PostgreSQL', 'Docker', 'AWS',
    'Metodologías Ágiles', 'Git', 'Tailwind CSS'
  ],
  habilidades_faltantes: ['Kubernetes', 'GraphQL', 'Microservicios'],
  sugerencias: [
    {
      titulo: 'Cuantifica tus logros',
      descripcion: 'En lugar de "Desarrollé APIs", usa "Desarrollé APIs que redujeron el tiempo de respuesta en un 30%".',
    },
    {
      titulo: 'Optimización de Keywords',
      descripcion: 'Añade "Cloud Native" y "Arquitectura" para mejorar el match con filtros ATS en Ecuador.',
    },
    {
      titulo: 'Formato de Contacto',
      descripcion: 'Asegúrate de incluir tu perfil de LinkedIn y ubicación (Ej: Quito, EC).',
    },
    {
      titulo: 'Sección de Proyectos',
      descripcion: 'Destaca tu participación en proyectos locales o open source.',
    },
  ],
};

export default function CVAnalysisPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzed, setIsAnalyzed] = useState(true); // Show mock by default
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
              <p className="text-xs text-muted-foreground mt-4">
                Máximo 10MB (PDF, DOCX)
              </p>
            </div>
          </div>
        </div>

        {/* Analysis Results */}
        {isAnalyzed && (
          <div className="grid lg:grid-cols-2 gap-6 max-w-5xl mx-auto">
            {/* Compatibility Score */}
            <div className="glass-card p-6">
              <h3 className="text-caption text-muted-foreground uppercase mb-4">
                COMPATIBILIDAD CON EL MERCADO
              </h3>
              <div className="flex items-center gap-6">
                <div className="relative w-32 h-32">
                  <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                    <circle
                      cx="18" cy="18" r="15.5"
                      fill="none"
                      stroke="hsl(var(--secondary))"
                      strokeWidth="3"
                    />
                    <circle
                      cx="18" cy="18" r="15.5"
                      fill="none"
                      stroke="hsl(var(--primary))"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeDasharray={`${mockAnalysis.compatibilidad} 100`}
                    />
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-3xl font-bold">{mockAnalysis.compatibilidad}%</span>
                    <span className="text-xs text-muted-foreground">Nivel {mockAnalysis.seniority}</span>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">
                  Tu perfil tiene una alta demanda en el sector bancario y fintech de Ecuador.
                </p>
              </div>
            </div>

            {/* Skills Detected */}
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-h3">Habilidades Detectadas</h3>
                <Badge className="bg-success/20 text-success border-success/30">
                  {mockAnalysis.habilidades_detectadas.length} Encontradas
                </Badge>
              </div>
              <div className="flex flex-wrap gap-2 mb-6">
                {mockAnalysis.habilidades_detectadas.map((skill) => (
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
                  {mockAnalysis.habilidades_faltantes.map((skill) => (
                    <Badge key={skill} variant="outline" className="border-warning/50 text-warning">
                      {skill}
                    </Badge>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground mt-3">
                  Estas habilidades son mencionadas en el 40% de las vacantes actuales para tu rol.
                </p>
              </div>
            </div>

            {/* Improvement Suggestions */}
            <div className="glass-card p-6 lg:col-span-2">
              <div className="flex items-center gap-2 mb-6">
                <Lightbulb className="h-5 w-5 text-warning" />
                <h3 className="text-h3">Sugerencias de Mejora</h3>
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                {mockAnalysis.sugerencias.map((suggestion, index) => (
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
