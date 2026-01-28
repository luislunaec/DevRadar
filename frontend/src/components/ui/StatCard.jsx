import React from 'react';

const StatCard = ({ title, value, icon, trend, trendColor }) => {
  return (
    <div className="bg-slate-800/40 backdrop-blur-md border border-slate-700 p-6 rounded-3xl shadow-xl hover:border-blue-500/50 transition-all group">
      <div className="flex justify-between items-start mb-4">
        <div className="p-3 bg-blue-600/20 rounded-2xl text-blue-400 group-hover:scale-110 transition-transform">
          {icon}
        </div>
        <span className={`text-xs font-bold px-2 py-1 rounded-lg ${trendColor} bg-opacity-20`}>
          {trend}
        </span>
      </div>
      <div>
        <p className="text-slate-400 text-sm font-medium">{title}</p>
        <h3 className="text-3xl font-bold text-white mt-1">{value}</h3>
      </div>
    </div>
  );
};

export default StatCard;