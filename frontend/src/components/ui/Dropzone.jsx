import { Upload, FileText } from 'lucide-react';

const Dropzone = ({ onFileUpload }) => {
  return (
    <div className="w-full border-2 border-dashed border-slate-700 rounded-3xl p-10 flex flex-col items-center justify-center bg-slate-800/20 hover:bg-blue-600/5 hover:border-blue-500/50 transition-all cursor-pointer group">
      <div className="p-4 bg-slate-800 rounded-2xl group-hover:scale-110 transition-transform shadow-xl mb-4">
        <Upload className="text-blue-500" size={32} />
      </div>
      <h4 className="text-white font-bold text-lg">Arrastra tu CV aquí</h4>
      <p className="text-slate-500 text-sm mt-1">Soporta PDF o Word (Máx. 5MB)</p>
      <button className="mt-6 px-6 py-2 bg-slate-800 text-white rounded-xl text-sm font-medium border border-slate-700 hover:bg-slate-700 transition-colors">
        Seleccionar archivo
      </button>
    </div>
  );
};

export default Dropzone;