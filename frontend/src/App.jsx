import { useState } from 'react';
// IMPORTANTE: Verifica que estos archivos existan en src/components/
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import Footer from './components/Footer';
import { Search } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('buscador');

  return (
    <div className="flex h-screen bg-slate-950 text-white overflow-hidden">
      {/* Si esto falla, el problema es Sidebar.jsx */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Si esto falla, el problema es Header.jsx */}
        <Header />

        <main className="flex-1 relative overflow-y-auto bg-slate-900/30 p-6">
          <div className="h-full w-full flex items-center justify-center">
            
            {activeTab === 'buscador' && (
              <div className="text-center space-y-6">
                <h1 className="text-4xl font-bold">Buscador DevRadar</h1>
                <div className="flex bg-slate-800 p-2 rounded-xl border border-slate-700">
                   <input 
                    type="text" 
                    placeholder="Busca un cargo..."
                    className="bg-transparent p-2 outline-none w-64"
                   />
                   <button className="bg-blue-600 px-4 py-2 rounded-lg">Buscar</button>
                </div>
              </div>
            )}

            {/* Si esto falla, el problema es Dashboard.jsx o StatCard.jsx */}
            {activeTab === 'dashboard' && <Dashboard />}

            {!['buscador', 'dashboard'].includes(activeTab) && (
              <h2 className="text-2xl text-slate-500">Sección {activeTab} en construcción</h2>
            )}
            
          </div>
        </main>

        {/* Si esto falla, el problema es Footer.jsx */}
        <Footer />
      </div>
    </div>
  );
}