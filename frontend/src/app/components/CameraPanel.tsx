import { useState } from 'react';
import { Video, Play, Square, Camera, AlertCircle } from 'lucide-react';

export function CameraPanel() {
  const [selectedCamera, setSelectedCamera] = useState('cam-001');
  const [isStreaming, setIsStreaming] = useState(false);

  const cameras = [
    { id: 'cam-001', name: 'Cámara Entrada Principal' },
    { id: 'cam-002', name: 'Cámara Estacionamiento' },
    { id: 'cam-003', name: 'Cámara Perímetro Norte' },
    { id: 'cam-004', name: 'Cámara Perímetro Sur' },
  ];

  const recentAlerts = [
    { id: 1, time: '14:32', message: 'Movimiento detectado - Zona Norte', severity: 'warning' },
    { id: 2, time: '14:15', message: 'Acceso no autorizado - Entrada B', severity: 'danger' },
    { id: 3, time: '13:58', message: 'Zona de riesgo activada - Centro', severity: 'danger' },
  ];

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Stream en Vivo */}
      <div className="bg-slate-800 rounded-lg p-4">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <Video className="w-5 h-5 text-blue-400" />
          STREAM EN VIVO
        </h3>

        {/* Selector de cámara */}
        <select
          value={selectedCamera}
          onChange={(e) => setSelectedCamera(e.target.value)}
          className="w-full mb-3 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
        >
          {cameras.map(camera => (
            <option key={camera.id} value={camera.id}>
              {camera.name}
            </option>
          ))}
        </select>

        {/* Área de video */}
        <div className="aspect-video bg-slate-900 rounded-lg mb-3 relative overflow-hidden">
          {isStreaming ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mb-2 mx-auto"></div>
                <p className="text-sm text-slate-400">Transmitiendo en vivo...</p>
              </div>
            </div>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <Camera className="w-12 h-12 text-slate-600" />
            </div>
          )}
        </div>

        {/* Controles */}
        <div className="flex gap-2">
          {!isStreaming ? (
            <button
              onClick={() => setIsStreaming(true)}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
            >
              <Play className="w-4 h-4" />
              Ver en vivo
            </button>
          ) : (
            <button
              onClick={() => setIsStreaming(false)}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
            >
              <Square className="w-4 h-4" />
              Parar
            </button>
          )}
        </div>
      </div>

      {/* Últimas Detecciones */}
      <div className="bg-slate-800 rounded-lg p-4 flex-1">
        <h3 className="font-semibold mb-3 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-orange-400" />
          ÚLTIMA DETECCIÓN
        </h3>

        <div className="space-y-2">
          {recentAlerts.map(alert => (
            <div
              key={alert.id}
              className={`p-3 rounded-lg ${
                alert.severity === 'danger'
                  ? 'bg-red-900/30 border border-red-700/50'
                  : 'bg-yellow-900/30 border border-yellow-700/50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm">{alert.message}</p>
                  <p className="text-xs text-slate-400 mt-1">{alert.time}</p>
                </div>
                <div className={`w-2 h-2 rounded-full ${
                  alert.severity === 'danger' ? 'bg-red-500' : 'bg-yellow-500'
                }`}></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
