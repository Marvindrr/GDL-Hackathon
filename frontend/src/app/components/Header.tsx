import { Building2 } from 'lucide-react';

export function Header() {
  return (
    <header className="bg-slate-900 text-white border-b border-slate-700 px-6 py-4">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-2">
          <Building2 className="w-8 h-8 text-blue-400" />
          <span className="font-bold text-xl">SecureVision</span>
        </div>

        <nav className="flex items-center gap-6">
          <button className="hover:text-blue-400 transition-colors">
            Zonas de riesgo
          </button>
          <button className="hover:text-blue-400 transition-colors">
            Gráficas
          </button>
          <button className="hover:text-blue-400 transition-colors">
            Reportes
          </button>
          <button className="hover:text-blue-400 transition-colors">
            Cámaras
          </button>
          <button className="px-4 py-1 bg-blue-600 hover:bg-blue-700 rounded transition-colors">
            GDL
          </button>
        </nav>
      </div>
    </header>
  );
}
