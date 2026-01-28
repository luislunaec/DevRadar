import { Search } from 'lucide-react';

const Buscador = () => {
  return (
    <div className="w-full max-w-3xl text-center space-y-10 animate-in fade-in zoom-in duration-500">
      <div className="space-y-4">
        <h2 className="text-5xl md:text-6xl font-extrabold text-white tracking-tight leading-tight">
          Encuentra tu próximo <br />
          <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            reto tecnológico
          </span>
        </h2>
        <p className="text-slate-400 text-lg">
          Analizamos la demanda real del mercado para potenciar tu carrera.
        </p>
      </div>

      {/* Barra de Búsqueda */}
      <div className="relative group">
        <div className="absolute -inset-1 bg-blue-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition"></div>
        <div className="relative flex items-center bg-slate-800 border border-slate-700 p-2 rounded-2xl shadow-2xl">
          <Search className="ml-4 text-slate-500" size={24} />
          <input 
            type="text" 
            placeholder="Ej: Senior React Developer..."
            className="w-full bg-transparent p-4 text-xl text-white placeholder-slate-500 focus:outline-none"
          />
          <button className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-xl font-bold transition-all shadow-lg active:scale-95">
            Buscar
          </button>
        </div>
      </div>

      {/* Tags de ejemplo */}
      <div className="flex justify-center gap-4 text-xs font-mono text-slate-500">
        <span className="hover:text-blue-400 cursor-pointer">#DATA_SCIENCE</span>
        <span className="hover:text-blue-400 cursor-pointer">#FRONTEND</span>
        <span className="hover:text-blue-400 cursor-pointer">#CLOUD_ARCHITECT</span>
      </div>
    </div>
  );
};

export default Buscador;