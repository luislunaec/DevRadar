import React, { useState } from 'react';
import { 
  LayoutDashboard, Search, Wrench, MessageSquare, 
  FileText, ChevronLeft, ChevronRight, LogOut 
} from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const [isCollapsed, setIsCollapsed] = useState(true);

  const menuItems = [
    { id: 'buscador', label: 'Buscador', icon: <Search size={22} /> },
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={22} /> },
    { id: 'herramientas', label: 'Herramientas', icon: <Wrench size={22} /> },
    { id: 'chatbot', label: 'Preguntas IA', icon: <MessageSquare size={22} /> },
    { id: 'cv-analysis', label: 'Analizador CV', icon: <FileText size={22} /> },
  ];

  return (
    <div 
      className={`h-screen bg-slate-950 text-white transition-all duration-300 flex flex-col border-r border-slate-800 ${
        isCollapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Botón para retraer */}
      <button 
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="p-4 hover:bg-slate-800 flex justify-end text-slate-400"
      >
        {isCollapsed ? <ChevronRight size={24} /> : <ChevronLeft size={24} />}
      </button>

      {/* Logo / Título */}
      <div className={`px-6 py-4 mb-8 ${isCollapsed ? 'hidden' : 'block'}`}>
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
          DevRadar
        </h1>
        <p className="text-xs text-slate-500">Talent Intelligence</p>
      </div>

      {/* Menú */}
      <nav className="flex-1 px-3 space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center p-3 rounded-lg transition-colors ${
              activeTab === item.id 
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50' 
                : 'text-slate-400 hover:bg-slate-900 hover:text-white'
            }`}
          >
            <div className="min-w-[30px]">{item.icon}</div>
            {!isCollapsed && <span className="ml-3 font-medium">{item.label}</span>}
          </button>
        ))}
      </nav>

      {/* Logout al final */}
      <div className="p-4 border-t border-slate-900">
        <button className="flex items-center text-slate-500 hover:text-red-400 p-2">
          <LogOut size={22} />
          {!isCollapsed && <span className="ml-3">Cerrar Sesión</span>}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;