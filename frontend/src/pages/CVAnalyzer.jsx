import { useState } from 'react';
import { AlertTriangle, CheckCircle2, Lightbulb } from 'lucide-react';
import Dropzone from '../components/ui/Dropzone';
import CompatibilityCircle from '../components/ui/CompatibilityCircle';

const CVAnalyzer = () => {
  const [isAnalyzed, setIsAnalyzed] = useState(false);

  return (
    <div className="w-full max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-20">
      {/* Header de Sección */}
      <header className="text-left space-y-2">
        <h2 className="text-4xl font-extrabold text-white">Analizador de Perfil <span className="text-blue-500">IA</span></h2>
        <p className="text-slate-400 max-w-2xl text-lg">
          Comparamos tu experiencia técnica con la demanda real del mercado laboral IT de este mes.
        </p>
      </header>

      {!isAnalyzed ? (
        <div onClick={() => setIsAnalyzed(true)}> {/* Simulación de carga */}
          <Dropzone />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Columna Izquierda: Score y Resumen */}
          <div className="space-y-6">
            <CompatibilityCircle percentage={78} />
            <div className="p-6 bg-blue-600/10 border border-blue-500/20 rounded-3xl">
              <p className="text-slate-300 text-sm italic leading-relaxed">
                "Tu perfil tiene una demanda **Alta** en el sector Fintech y E-commerce. Posees las bases sólidas, pero el mercado está transicionando hacia arquitecturas Serverless."
              </p>
            </div>
          </div>

          {/* Columna Derecha: Skills y Mejoras */}
          <div className="lg:col-span-2 space-y-8">
            {/* Skills Detectadas */}
            <section className="bg-slate-800/20 p-6 rounded-3xl border border-slate-800">
              <div className="flex items-center gap-2 mb-4 text-emerald-400">
                <CheckCircle2 size={18} />
                <h4 className="font-bold text-sm uppercase tracking-wider">Habilidades Detectadas</h4>
              </div>
              <div className="flex flex-wrap gap-2">
                {['React', 'Tailwind', 'Node.js', 'Git'].map(skill => (
                  <span key={skill} className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-lg text-sm">{skill}</span>
                ))}
              </div>
            </section>

            {/* Skill Gaps */}
            <section className="bg-slate-800/20 p-6 rounded-3xl border border-slate-800">
              <div className="flex items-center gap-2 mb-4 text-amber-400">
                <AlertTriangle size={18} />
                <h4 className="font-bold text-sm uppercase tracking-wider">Habilidades Faltantes (Skill Gaps)</h4>
              </div>
              <div className="flex flex-wrap gap-2">
                {['TypeScript', 'Docker', 'Testing (Jest)'].map(skill => (
                  <span key={skill} className="px-3 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-lg text-sm">{skill}</span>
                ))}
              </div>
            </section>

            {/* Sugerencias de Mejora */}
            <section className="space-y-4">
              <div className="flex items-center gap-2 text-white">
                <Lightbulb className="text-blue-500" size={20} />
                <h4 className="font-bold">Recomendaciones del Analista</h4>
              </div>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <li className="p-4 bg-slate-800/40 rounded-2xl text-slate-300 text-sm border-l-4 border-blue-500">
                  Incluye métricas de rendimiento en tus proyectos (ej. "Mejoré la carga en un 20%").
                </li>
                <li className="p-4 bg-slate-800/40 rounded-2xl text-slate-300 text-sm border-l-4 border-blue-500">
                  Agrega un enlace a tu repositorio de GitHub o Portafolio.
                </li>
              </ul>
            </section>

            <button 
              onClick={() => setIsAnalyzed(false)}
              className="w-full py-4 text-slate-500 hover:text-white transition-colors text-sm font-medium"
            >
              Cargar otro archivo
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CVAnalyzer;