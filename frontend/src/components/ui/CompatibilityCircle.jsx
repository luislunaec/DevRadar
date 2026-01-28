const CompatibilityCircle = ({ percentage }) => {
  const radius = 70;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-slate-800/40 rounded-3xl border border-slate-700 shadow-xl">
      <div className="relative flex items-center justify-center mb-4">
        <svg height={radius * 2} width={radius * 2}>
          <circle stroke="#1e293b" fill="transparent" strokeWidth={stroke} r={normalizedRadius} cx={radius} cy={radius} />
          <circle
            stroke="#3b82f6" fill="transparent" strokeWidth={stroke} strokeDasharray={circumference + ' ' + circumference}
            style={{ strokeDashoffset, transition: 'stroke-dashoffset 1s ease-in-out' }}
            strokeLinecap="round" r={normalizedRadius} cx={radius} cy={radius}
          />
        </svg>
        <span className="absolute text-3xl font-bold text-white font-mono">{percentage}%</span>
      </div>
      <p className="text-blue-400 font-bold uppercase tracking-widest text-xs">Compatibilidad</p>
    </div>
  );
};

export default CompatibilityCircle;