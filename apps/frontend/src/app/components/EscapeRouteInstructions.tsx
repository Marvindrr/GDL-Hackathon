import { Navigation, ArrowRight, AlertTriangle } from 'lucide-react';

export function EscapeRouteInstructions() {
  const escapeSteps = [
    'Diríjase a la salida de emergencia más cercana marcada en el mapa',
    'Siga las señales luminosas en el piso hacia la Zona Segura A',
    'Evite la Zona Centro - Alto riesgo detectado',
    'Punto de reunión: Estacionamiento Norte'
  ];

  return (
    <div className="bg-gradient-to-r from-orange-900/40 to-red-900/40 border border-orange-700/50 rounded-lg p-6">
      <div className="flex items-start gap-4">
        <div className="flex items-center gap-3 mb-4">
          <Navigation className="w-6 h-6 text-orange-400 animate-pulse" />
          <h3 className="font-bold text-lg">INSTRUCCIONES DE RUTA DE ESCAPE</h3>
          <AlertTriangle className="w-6 h-6 text-red-400 animate-pulse" />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {escapeSteps.map((step, index) => (
          <div key={index} className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 bg-orange-600 rounded-full flex items-center justify-center font-bold">
              {index + 1}
            </div>
            <div className="flex-1">
              <p className="text-sm">{step}</p>
            </div>
            {index < escapeSteps.length - 1 && (
              <ArrowRight className="w-5 h-5 text-orange-400 flex-shrink-0 mt-1" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
