import React from 'react';
import { Bell, User } from 'lucide-react';

const Header = () => {
  return (
    <header className="w-full flex justify-between items-center py-4 px-8 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-30">
      <div className="text-slate-400 text-sm font-medium">
        Bienvenido, <span className="text-white">User</span> 👋
      </div>
    </header>
  );
};

export default Header;