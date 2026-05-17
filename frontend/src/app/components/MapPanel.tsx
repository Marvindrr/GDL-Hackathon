import { useState } from 'react';
import { Search, MapPin, AlertTriangle } from 'lucide-react';

export function MapPanel() {
  const [searchZone, setSearchZone] = useState('');

  const riskZones = [
    { id: 1, name: 'Zona Centro', level: 'Alto', color: 'bg-red-500' },
    { id: 2, name: 'Zona Norte', level: 'Medio', color: 'bg-yellow-500' },
    { id: 3, name: 'Zona Sur', level: 'Bajo', color: 'bg-green-500' },
  ];

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Mapa Principal */}
      <div className="flex-1 bg-slate-800 rounded-lg relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-slate-500 text-center">
            <MapPin className="w-16 h-16 mx-auto mb-2" />
            <p>Mapa Interactivo</p>
            <p className="text-sm">Guadalajara, México</p>
          </div>
        </div>

        {/* Simulación de pins de zonas */}
        <div className="absolute top-1/4 left-1/3 w-4 h-4 bg-red-500 rounded-full animate-pulse"></div>
        <div className="absolute top-1/2 right-1/3 w-4 h-4 bg-yellow-500 rounded-full animate-pulse"></div>
        <div className="absolute bottom-1/3 left-1/2 w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
      </div>

      {/* Buscador de zonas */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchZone}
            onChange={(e) => setSearchZone(e.target.value)}
            placeholder="Buscar zona..."
            className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>
        <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
          Buscar
        </button>
      </div>

      {/* Botón zonas de riesgo */}
      <button className="flex items-center gap-2 px-4 py-3 bg-orange-600 hover:bg-orange-700 rounded-lg transition-colors">
        <AlertTriangle className="w-5 h-5" />
        Ver Zonas de Riesgo
      </button>

      {/* Niveles de riesgo */}
      <div className="bg-slate-800 rounded-lg p-4">
        <h3 className="font-semibold mb-3">Niveles de Riesgo Actuales</h3>
        <div className="space-y-2">
          {riskZones.map(zone => (
            <div key={zone.id} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${zone.color}`}></div>
                <span className="text-sm">{zone.name}</span>
              </div>
              <span className="text-sm text-slate-400">{zone.level}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
