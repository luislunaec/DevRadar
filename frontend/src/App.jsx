import { useState } from 'react';

// Layout (Estructura Global)
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';

// Pages (Contenido de cada sección)
import Buscador from './pages/Buscador';
import Dashboard from './pages/Dashboard';
import CVAnalysis from './pages/CVAnalyzer';

export default function App() {
  const [activeTab, setActiveTab] = useState('buscador');

  return (
    <div className="flex h-screen bg-slate-950 text-white overflow-hidden font-sans">
      {/* Sidebar Fijo */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Contenedor Principal */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        
        <Header />

        <main className="flex-1 relative overflow-y-auto bg-slate-900/30">
          {/* Fondo decorativo (Efecto de luz azul) */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-blue-600/5 rounded-full blur-[120px]"></div>
          </div>

          <div className="min-h-full flex items-center justify-center p-6 md:p-12">
            
            {/* Sistema de Rutas Simple (Cambia la página según el Tab) */}
            {activeTab === 'buscador' && <Buscador />}
            
            {activeTab === 'dashboard' && <Dashboard />}
            
            {activeTab === 'cv-analysis' && <CVAnalysis />}

            {/* Mensaje para pestañas que aún no creamos como Page */}
            {!['buscador', 'dashboard', 'cv-analysis'].includes(activeTab) && (
              <div className="text-center">
                <h2 className="text-2xl text-slate-600 font-mono italic">
                  &gt; SECCIÓN_{activeTab.toUpperCase()}_EN_DESARROLLO
                </h2>
              </div>
            )}
          </div>
        </main>

        <Footer />
      </div>
    </div>
  );
}