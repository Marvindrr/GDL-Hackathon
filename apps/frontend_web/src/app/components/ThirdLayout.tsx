import { useState } from 'react';
import {
  Shield,
  MapPin,
  Video,
  AlertTriangle,
  Search,
  Play,
  Square,
  Activity,
  Navigation,
  Bell,
  Settings,
  Users,
  Database,
  Zap,
  Camera,
  ChevronDown,
  X
} from 'lucide-react';

export function ThirdLayout() {
  const [selectedCamera, setSelectedCamera] = useState('cam-001');
  const [isStreaming, setIsStreaming] = useState(true);
  const [showEscapeRoute, setShowEscapeRoute] = useState(true);
  const [selectedZone, setSelectedZone] = useState('');

  const cameras = [
    { id: 'cam-001', name: 'Entrada Principal', zone: 'Centro', status: 'online' },
    { id: 'cam-002', name: 'Estacionamiento A', zone: 'Norte', status: 'online' },
    { id: 'cam-003', name: 'Perímetro Norte', zone: 'Norte', status: 'online' },
    { id: 'cam-004', name: 'Salida Emergencia', zone: 'Sur', status: 'offline' },
  ];

  const riskZones = [
    { id: 1, name: 'Centro', level: 'Crítico', percentage: 85, color: 'from-rose-600 to-red-600', dotColor: 'bg-red-500' },
    { id: 2, name: 'Norte', level: 'Moderado', percentage: 45, color: 'from-amber-600 to-orange-600', dotColor: 'bg-orange-500' },
    { id: 3, name: 'Sur', level: 'Seguro', percentage: 15, color: 'from-emerald-600 to-green-600', dotColor: 'bg-green-500' },
    { id: 4, name: 'Este', level: 'Bajo', percentage: 25, color: 'from-cyan-600 to-blue-600', dotColor: 'bg-blue-500' },
  ];

  const recentAlerts = [
    { id: 1, time: '14:32:18', message: 'Movimiento no autorizado detectado', zone: 'Norte', type: 'motion', severity: 'warning' },
    { id: 2, time: '14:15:42', message: 'Intento de acceso denegado', zone: 'Centro', type: 'access', severity: 'critical' },
    { id: 3, time: '13:58:05', message: 'Cámara 4 desconectada', zone: 'Sur', type: 'system', severity: 'info' },
    { id: 4, time: '13:45:33', message: 'Zona de alto riesgo activada', zone: 'Centro', type: 'risk', severity: 'critical' },
  ];

  return (
    <div className="size-full flex flex-col bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Top Header Bar */}
      <div className="bg-gradient-to-r from-indigo-950 via-indigo-900 to-purple-950 border-b border-indigo-700/30 shadow-lg">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Title */}
            <div className="flex items-center gap-4">
              <div className="p-2 bg-indigo-600 rounded-lg">
                <Shield className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-indigo-200 bg-clip-text text-transparent">
                  SECUREVISION PRO
                </h1>
                <p className="text-sm text-indigo-300">Sistema de Monitoreo Avanzado - Guadalajara</p>
              </div>
            </div>

            {/* Search Bar */}
            <div className="flex-1 max-w-xl mx-8">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-indigo-400" />
                <input
                  type="text"
                  value={selectedZone}
                  onChange={(e) => setSelectedZone(e.target.value)}
                  placeholder="Buscar zona, cámara, incidente..."
                  className="w-full pl-12 pr-4 py-3 bg-indigo-950/50 border border-indigo-700/50 rounded-xl placeholder-indigo-400 focus:outline-none focus:border-indigo-500 focus:bg-indigo-950/70 transition-all"
                />
              </div>
            </div>

            {/* Status Indicators */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-4 py-2 bg-indigo-950/50 rounded-lg border border-indigo-700/30">
                <Activity className="w-5 h-5 text-green-400" />
                <div>
                  <p className="text-xs text-indigo-300">Sistema</p>
                  <p className="text-sm font-semibold text-green-400">Operacional</p>
                </div>
              </div>

              <button className="relative p-3 hover:bg-indigo-950/50 rounded-lg transition-colors">
                <Bell className="w-6 h-6 text-indigo-300" />
                <span className="absolute top-2 right-2 w-3 h-3 bg-red-500 rounded-full border-2 border-indigo-900 animate-pulse"></span>
              </button>

              <button className="p-3 hover:bg-indigo-950/50 rounded-lg transition-colors">
                <Settings className="w-6 h-6 text-indigo-300" />
              </button>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="px-6 pb-3 flex items-center gap-2">
          <button className="px-6 py-2 bg-indigo-600 rounded-t-lg font-semibold shadow-lg">
            Vista Principal
          </button>
          <button className="px-6 py-2 hover:bg-indigo-950/50 rounded-t-lg transition-colors text-indigo-300">
            Zonas de Riesgo
          </button>
          <button className="px-6 py-2 hover:bg-indigo-950/50 rounded-t-lg transition-colors text-indigo-300">
            Análisis
          </button>
          <button className="px-6 py-2 hover:bg-indigo-950/50 rounded-t-lg transition-colors text-indigo-300">
            Reportes
          </button>
          <button className="px-6 py-2 hover:bg-indigo-950/50 rounded-t-lg transition-colors text-indigo-300">
            Histórico
          </button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="flex-1 grid grid-cols-2 gap-6 p-6 overflow-hidden">
        {/* Left Side - Map Panel (50%) */}
        <div className="flex flex-col gap-4 overflow-hidden">
          {/* Large Map */}
          <div className="flex-1 bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-cyan-700/30 shadow-2xl overflow-hidden relative">
            {/* Map Header */}
            <div className="absolute top-4 left-4 right-4 z-10 flex items-center justify-between">
              <div className="bg-slate-900/90 backdrop-blur-md px-4 py-3 rounded-xl border border-cyan-600/50 shadow-lg">
                <h3 className="font-bold flex items-center gap-2 text-cyan-400">
                  <MapPin className="w-5 h-5" />
                  MAPA INTERACTIVO
                </h3>
              </div>

              <div className="flex gap-2">
                <button className="px-4 py-2 bg-slate-900/90 backdrop-blur-md hover:bg-slate-800 rounded-xl border border-cyan-600/50 transition-colors">
                  <span className="text-sm">Vista Satélite</span>
                </button>
                <button className="px-4 py-2 bg-slate-900/90 backdrop-blur-md hover:bg-slate-800 rounded-xl border border-cyan-600/50 transition-colors">
                  <span className="text-sm">Capas</span>
                </button>
              </div>
            </div>

            {/* Map Content */}
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
              <div className="text-slate-600 text-center">
                <MapPin className="w-32 h-32 mx-auto mb-4 opacity-20" />
                <p className="text-lg font-semibold">Sistema de Geolocalización</p>
                <p className="text-sm">Monitoreo en Tiempo Real</p>
              </div>
            </div>

            {/* Risk Zone Markers on Map */}
            <div className="absolute top-1/4 left-1/3 group cursor-pointer">
              <div className="relative">
                <div className="w-8 h-8 bg-red-500 rounded-full animate-pulse shadow-lg shadow-red-500/50"></div>
                <div className="absolute inset-0 w-8 h-8 bg-red-500 rounded-full animate-ping opacity-75"></div>
              </div>
              <div className="absolute hidden group-hover:block top-full left-1/2 -translate-x-1/2 mt-3 bg-slate-900 px-4 py-3 rounded-xl border border-red-500/50 shadow-xl whitespace-nowrap z-20">
                <p className="text-sm font-bold text-red-400">⚠ ZONA CENTRO - CRÍTICO</p>
                <p className="text-xs text-slate-400 mt-1">5 incidentes activos • 85% riesgo</p>
              </div>
            </div>

            <div className="absolute top-1/2 right-1/4 group cursor-pointer">
              <div className="relative">
                <div className="w-7 h-7 bg-orange-500 rounded-full animate-pulse shadow-lg shadow-orange-500/50"></div>
                <div className="absolute inset-0 w-7 h-7 bg-orange-500 rounded-full animate-ping opacity-75"></div>
              </div>
              <div className="absolute hidden group-hover:block top-full left-1/2 -translate-x-1/2 mt-3 bg-slate-900 px-4 py-3 rounded-xl border border-orange-500/50 shadow-xl whitespace-nowrap z-20">
                <p className="text-sm font-bold text-orange-400">⚠ ZONA NORTE - MODERADO</p>
                <p className="text-xs text-slate-400 mt-1">2 incidentes activos • 45% riesgo</p>
              </div>
            </div>

            <div className="absolute bottom-1/3 left-1/2 group cursor-pointer">
              <div className="relative">
                <div className="w-6 h-6 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
              </div>
              <div className="absolute hidden group-hover:block top-full left-1/2 -translate-x-1/2 mt-3 bg-slate-900 px-4 py-3 rounded-xl border border-green-500/50 shadow-xl whitespace-nowrap z-20">
                <p className="text-sm font-bold text-green-400">✓ ZONA SUR - SEGURO</p>
                <p className="text-xs text-slate-400 mt-1">Sin incidentes • 15% riesgo</p>
              </div>
            </div>

            {/* Map Controls */}
            <div className="absolute bottom-6 right-6 flex flex-col gap-2">
              <button className="p-3 bg-slate-900/90 backdrop-blur-md hover:bg-slate-800 rounded-xl border border-cyan-600/50 transition-colors shadow-lg">
                <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </button>
              <button className="p-3 bg-slate-900/90 backdrop-blur-md hover:bg-slate-800 rounded-xl border border-cyan-600/50 transition-colors shadow-lg">
                <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                </svg>
              </button>
              <button className="p-3 bg-slate-900/90 backdrop-blur-md hover:bg-slate-800 rounded-xl border border-cyan-600/50 transition-colors shadow-lg">
                <svg className="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5" />
                </svg>
              </button>
            </div>
          </div>

          {/* Escape Route Alert */}
          {showEscapeRoute && (
            <div className="bg-gradient-to-r from-rose-600 via-red-600 to-orange-600 rounded-2xl p-5 border border-red-400/30 shadow-2xl shadow-red-900/50 relative">
              <button
                onClick={() => setShowEscapeRoute(false)}
                className="absolute top-3 right-3 p-1 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white/20 rounded-xl">
                  <Navigation className="w-8 h-8 animate-pulse" />
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-xl mb-1">⚠ RUTA DE EVACUACIÓN ACTIVA</h3>
                  <p className="text-sm opacity-95">
                    <strong>Salida:</strong> Puerta Norte • <strong>Distancia:</strong> 150m • <strong>Tiempo:</strong> 2 min • <strong>Evitar:</strong> Zona Centro
                  </p>
                </div>
                <button className="px-6 py-3 bg-white text-red-600 font-bold rounded-xl hover:bg-red-50 transition-colors shadow-lg">
                  Ver Detalles
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Side - Camera Panel (50%) */}
        <div className="flex flex-col gap-4 overflow-hidden">
          {/* Large Camera Feed */}
          <div className="flex-1 bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-purple-700/30 shadow-2xl overflow-hidden">
            <div className="h-full flex flex-col p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold flex items-center gap-2 text-purple-400">
                  <Video className="w-6 h-6" />
                  MONITOREO EN VIVO
                </h3>
                <div className="flex items-center gap-2 px-3 py-1 bg-red-600 rounded-full text-xs font-bold">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  TRANSMITIENDO
                </div>
              </div>

              {/* Large Video Display */}
              <div className="flex-1 bg-slate-950 rounded-xl mb-4 relative overflow-hidden border border-purple-600/30">
                {isStreaming ? (
                  <div className="absolute inset-0">
                    {/* Camera Info Overlay */}
                    <div className="absolute top-4 left-4 right-4 flex items-start justify-between z-10">
                      <div className="bg-slate-900/90 backdrop-blur-md px-4 py-2 rounded-xl border border-purple-600/50">
                        <p className="text-sm font-semibold">{cameras.find(c => c.id === selectedCamera)?.name}</p>
                        <p className="text-xs text-purple-400">{cameras.find(c => c.id === selectedCamera)?.zone}</p>
                      </div>
                      <div className="bg-slate-900/90 backdrop-blur-md px-3 py-2 rounded-xl border border-purple-600/50">
                        <p className="text-xs text-purple-400">14:32:45</p>
                      </div>
                    </div>

                    {/* Simulated Camera Feed */}
                    <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
                      <div className="text-center">
                        <Video className="w-24 h-24 text-slate-700 mx-auto mb-3" />
                        <p className="text-slate-500">Stream de video activo</p>
                        <p className="text-sm text-slate-600 mt-1">1920x1080 @ 30fps</p>
                      </div>
                    </div>

                    {/* Recording Indicator */}
                    <div className="absolute bottom-4 left-4 flex items-center gap-2 bg-slate-900/90 backdrop-blur-md px-3 py-2 rounded-xl border border-red-600/50">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                      <span className="text-xs font-semibold">GRABANDO</span>
                    </div>
                  </div>
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Camera className="w-24 h-24 text-slate-700" />
                  </div>
                )}
              </div>

              {/* Camera Controls */}
              <div className="flex gap-3">
                <select
                  value={selectedCamera}
                  onChange={(e) => setSelectedCamera(e.target.value)}
                  className="flex-1 px-4 py-3 bg-slate-950 border border-purple-700/50 rounded-xl focus:outline-none focus:border-purple-500 transition-all"
                >
                  {cameras.map(camera => (
                    <option key={camera.id} value={camera.id}>
                      {camera.name} - {camera.zone} {camera.status === 'online' ? '🟢' : '🔴'}
                    </option>
                  ))}
                </select>

                {!isStreaming ? (
                  <button
                    onClick={() => setIsStreaming(true)}
                    className="px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 rounded-xl font-bold transition-all shadow-lg shadow-green-900/50 flex items-center gap-2"
                  >
                    <Play className="w-5 h-5" />
                    Iniciar
                  </button>
                ) : (
                  <button
                    onClick={() => setIsStreaming(false)}
                    className="px-8 py-3 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 rounded-xl font-bold transition-all shadow-lg shadow-red-900/50 flex items-center gap-2"
                  >
                    <Square className="w-5 h-5" />
                    Detener
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Info Panel */}
      <div className="grid grid-cols-3 gap-4 px-6 pb-6">
        {/* Risk Zones */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-cyan-700/30 p-5 shadow-xl">
          <h3 className="font-bold mb-4 flex items-center gap-2 text-cyan-400">
            <AlertTriangle className="w-5 h-5" />
            NIVELES DE RIESGO
          </h3>
          <div className="space-y-3">
            {riskZones.map(zone => (
              <div key={zone.id} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${zone.dotColor} shadow-lg`}></div>
                    <span className="text-sm font-semibold">{zone.name}</span>
                  </div>
                  <span className="text-xs text-slate-400">{zone.percentage}%</span>
                </div>
                <div className="h-2 bg-slate-950 rounded-full overflow-hidden">
                  <div
                    className={`h-full bg-gradient-to-r ${zone.color} transition-all duration-500`}
                    style={{ width: `${zone.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-purple-700/30 p-5 shadow-xl">
          <h3 className="font-bold mb-4 flex items-center gap-2 text-purple-400">
            <Zap className="w-5 h-5" />
            ALERTAS RECIENTES
          </h3>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {recentAlerts.slice(0, 4).map(alert => (
              <div
                key={alert.id}
                className={`p-3 rounded-xl border ${
                  alert.severity === 'critical'
                    ? 'bg-red-900/20 border-red-700/50'
                    : alert.severity === 'warning'
                    ? 'bg-amber-900/20 border-amber-700/50'
                    : 'bg-cyan-900/20 border-cyan-700/50'
                }`}
              >
                <div className="flex items-start justify-between mb-1">
                  <p className="text-xs font-semibold flex-1">{alert.message}</p>
                  <span className={`w-2 h-2 rounded-full flex-shrink-0 mt-1 ${
                    alert.severity === 'critical' ? 'bg-red-500' :
                    alert.severity === 'warning' ? 'bg-amber-500' : 'bg-cyan-500'
                  }`}></span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <span>{alert.zone}</span>
                  <span>{alert.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Stats */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-indigo-700/30 p-5 shadow-xl">
          <h3 className="font-bold mb-4 flex items-center gap-2 text-indigo-400">
            <Database className="w-5 h-5" />
            ESTADÍSTICAS DEL SISTEMA
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-950 rounded-xl p-3 border border-indigo-700/30">
              <p className="text-xs text-slate-400 mb-1">Cámaras Activas</p>
              <p className="text-2xl font-bold text-green-400">3/4</p>
            </div>
            <div className="bg-slate-950 rounded-xl p-3 border border-indigo-700/30">
              <p className="text-xs text-slate-400 mb-1">Alertas Hoy</p>
              <p className="text-2xl font-bold text-amber-400">12</p>
            </div>
            <div className="bg-slate-950 rounded-xl p-3 border border-indigo-700/30">
              <p className="text-xs text-slate-400 mb-1">Zonas Monitoreadas</p>
              <p className="text-2xl font-bold text-cyan-400">4</p>
            </div>
            <div className="bg-slate-950 rounded-xl p-3 border border-indigo-700/30">
              <p className="text-xs text-slate-400 mb-1">Uptime</p>
              <p className="text-2xl font-bold text-green-400">99%</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
