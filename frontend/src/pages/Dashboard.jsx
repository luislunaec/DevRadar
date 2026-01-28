import React from 'react';
import { Users, DollarSign, Zap, TrendingUp, BarChart3 } from 'lucide-react';
import StatCard from '../components/ui/StatCard';

const Dashboard = () => {
  // Aquí es donde en el futuro llamarás a tu API de Node.js
  // const [data, setData] = useState([]);

  return (
    <div className="w-full max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Encabezado del Dashboard */}
      <header className="mb-10">
        <h2 className="text-4xl font-bold text-white tracking-tight">
          Market <span className="text-blue-500">Insights</span>
        </h2>
        <p className="text-slate-400 mt-2">Análisis de datos extraídos de LinkedIn y portales IT.</p>
      </header>

      {/* Grid de Tarjetas (KPIs) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <StatCard 
          title="Ofertas Analizadas" 
          value="1,284" 
          icon={<Users size={24} />} 
          trend="+12% este mes"
          trendColor="text-emerald-400 bg-emerald-400"
        />
        <StatCard 
          title="Salario Promedio" 
          value="$2,450" 
          icon={<DollarSign size={24} />} 
          trend="USD / Mensual"
          trendColor="text-blue-400 bg-blue-400"
        />
        <StatCard 
          title="Nivel de Demanda" 
          value="Muy Alta" 
          icon={<Zap size={24} />} 
          trend="React / Node.js"
          trendColor="text-amber-400 bg-amber-400"
        />
      </div>

      {/* Panel Principal de Gráficas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Contenedor para Gráfica de Sueldos */}
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700 p-8 rounded-3xl h-80 flex flex-col items-center justify-center relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-blue-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <BarChart3 className="text-slate-700 mb-4" size={60} />
            <p className="text-slate-500 font-medium">Tendencia de Salarios (Próximamente)</p>
        </div>

        {/* Contenedor para Top Skills */}
        <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700 p-8 rounded-3xl h-80 flex flex-col items-center justify-center relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-1 h-full bg-cyan-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <TrendingUp className="text-slate-700 mb-4" size={60} />
            <p className="text-slate-500 font-medium">Habilidades más demandadas</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;