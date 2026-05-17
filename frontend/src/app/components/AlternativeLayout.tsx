import { useState } from 'react';
import {
  Building2,
  MapPin,
  Video,
  AlertTriangle,
  Search,
  Play,
  Square,
  Camera,
  Navigation,
  TrendingUp,
  FileText,
  Monitor,
  ChevronLeft,
  ChevronRight,
  Bell,
  AlertCircle
} from 'lucide-react';

export function AlternativeLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedCamera, setSelectedCamera] = useState('cam-001');
  const [isStreaming, setIsStreaming] = useState(true);
  const [selectedZone, setSelectedZone] = useState('');

  const cameras = [
    { id: 'cam-001', name: 'Entrada Principal', status: 'online' },
    { id: 'cam-002', name: 'Estacionamiento', status: 'online' },
    { id: 'cam-003', name: 'Perímetro Norte', status: 'online' },
    { id: 'cam-004', name: 'Perímetro Sur', status: 'offline' },
  ];

  const riskZones = [
    { id: 1, name: 'Centro', level: 'Alto', incidents: 5, color: 'bg-red-500' },
    { id: 2, name: 'Norte', level: 'Medio', incidents: 2, color: 'bg-yellow-500' },
    { id: 3, name: 'Sur', level: 'Bajo', incidents: 0, color: 'bg-green-500' },
  ];

  const recentAlerts = [
    { id: 1, time: '14:32', message: 'Movimiento detectado', zone: 'Norte', severity: 'warning' },
    { id: 2, time: '14:15', message: 'Acceso no autorizado', zone: 'Centro', severity: 'danger' },
    { id: 3, time: '13:58', message: 'Cámara desconectada', zone: 'Sur', severity: 'info' },
  ];

  return (
    <div className="size-full flex bg-slate-950 text-white">
      {/* Sidebar */}
      <div
        className={`bg-slate-900 border-r border-slate-800 flex flex-col transition-all duration-300 ${
          sidebarCollapsed ? 'w-16' : 'w-72'
        }`}
      >
        {/* Logo */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <Building2 className="w-8 h-8 text-blue-400" />
              <div>
                <h1 className="font-bold text-lg">SecureVision</h1>
                <p className="text-xs text-slate-400">Guadalajara, MX</p>
              </div>
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
          >
            {sidebarCollapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
            <MapPin className="w-5 h-5 flex-shrink-0" />
            {!sidebarCollapsed && <span>Mapa Principal</span>}
          </button>

          <button className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-800 rounded-lg transition-colors">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            {!sidebarCollapsed && <span>Zonas de Riesgo</span>}
          </button>

          <button className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-800 rounded-lg transition-colors">
            <TrendingUp className="w-5 h-5 flex-shrink-0" />
            {!sidebarCollapsed && <span>Gráficas</span>}
          </button>

          <button className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-800 rounded-lg transition-colors">
            <FileText className="w-5 h-5 flex-shrink-0" />
            {!sidebarCollapsed && <span>Reportes</span>}
          </button>

          <button className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-800 rounded-lg transition-colors">
            <Monitor className="w-5 h-5 flex-shrink-0" />
            {!sidebarCollapsed && <span>Cámaras</span>}
          </button>
        </nav>

        {/* System Status */}
        {!sidebarCollapsed && (
          <div className="p-4 border-t border-slate-800">
            <div className="bg-slate-800 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-slate-400">Estado del Sistema</span>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              </div>
              <p className="text-xs text-green-400">Operacional</p>
            </div>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="bg-slate-900 border-b border-slate-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1">
              <h2 className="text-xl font-bold">Panel de Control - Guadalajara</h2>
              <div className="flex-1 max-w-md relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  value={selectedZone}
                  onChange={(e) => setSelectedZone(e.target.value)}
                  placeholder="Buscar zona, cámara o incidente..."
                  className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg placeholder-slate-400 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button className="relative p-2 hover:bg-slate-800 rounded-lg transition-colors">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <div className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm">En Línea</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Grid */}
        <div className="flex-1 grid grid-cols-3 gap-4 p-4 overflow-hidden">
          {/* Left: Large Map - 2 columns */}
          <div className="col-span-2 flex flex-col gap-4 overflow-hidden">
            {/* Map */}
            <div className="flex-1 bg-slate-900 rounded-xl border border-slate-800 overflow-hidden relative">
              <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur-sm px-4 py-2 rounded-lg border border-slate-700">
                <h3 className="font-semibold flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-blue-400" />
                  Mapa de Seguridad - GDL
                </h3>
              </div>

              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-slate-500 text-center">
                  <MapPin className="w-24 h-24 mx-auto mb-4 text-slate-700" />
                  <p className="text-lg">Mapa Interactivo</p>
                  <p className="text-sm">Sistema de monitoreo geolocalizado</p>
                </div>
              </div>

              {/* Zonas de riesgo en el mapa */}
              <div className="absolute top-1/4 left-1/4 group">
                <div className="w-6 h-6 bg-red-500 rounded-full animate-pulse cursor-pointer"></div>
                <div className="absolute hidden group-hover:block top-full left-1/2 -translate-x-1/2 mt-2 bg-slate-900 px-3 py-2 rounded-lg border border-red-500/50 whitespace-nowrap">
                  <p className="text-sm font-semibold text-red-400">Zona Centro - Alto Riesgo</p>
                  <p className="text-xs text-slate-400">5 incidentes activos</p>
                </div>
              </div>

              <div className="absolute top-1/2 right-1/4 group">
                <div className="w-6 h-6 bg-yellow-500 rounded-full animate-pulse cursor-pointer"></div>
                <div className="absolute hidden group-hover:block top-full left-1/2 -translate-x-1/2 mt-2 bg-slate-900 px-3 py-2 rounded-lg border border-yellow-500/50 whitespace-nowrap">
                  <p className="text-sm font-semibold text-yellow-400">Zona Norte - Riesgo Medio</p>
                  <p className="text-xs text-slate-400">2 incidentes activos</p>
                </div>
              </div>

              <div className="absolute bottom-1/3 left-1/2 group">
                <div className="w-6 h-6 bg-green-500 rounded-full animate-pulse cursor-pointer"></div>
                <div className="absolute hidden group-hover:block top-full left-1/2 -translate-x-1/2 mt-2 bg-slate-900 px-3 py-2 rounded-lg border border-green-500/50 whitespace-nowrap">
                  <p className="text-sm font-semibold text-green-400">Zona Sur - Bajo Riesgo</p>
                  <p className="text-xs text-slate-400">Sin incidentes</p>
                </div>
              </div>

              {/* Map Controls */}
              <div className="absolute bottom-4 right-4 flex flex-col gap-2">
                <button className="p-2 bg-slate-900/90 backdrop-blur-sm hover:bg-slate-800 rounded-lg border border-slate-700 transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </button>
                <button className="p-2 bg-slate-900/90 backdrop-blur-sm hover:bg-slate-800 rounded-lg border border-slate-700 transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Escape Route Banner */}
            <div className="bg-gradient-to-r from-orange-600 to-red-600 rounded-xl p-4 border border-orange-500">
              <div className="flex items-center gap-4">
                <Navigation className="w-8 h-8 animate-pulse flex-shrink-0" />
                <div className="flex-1">
                  <h3 className="font-bold text-lg mb-1">RUTA DE ESCAPE ACTIVA</h3>
                  <p className="text-sm opacity-90">Salida de emergencia norte - 150m | Tiempo estimado: 2 min | Evitar zona centro</p>
                </div>
                <button className="px-6 py-2 bg-white text-red-600 font-bold rounded-lg hover:bg-slate-100 transition-colors">
                  Ver Ruta
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Cameras and Alerts */}
          <div className="flex flex-col gap-4 overflow-hidden">
            {/* Live Camera Feed */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-4 flex-1 flex flex-col">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Video className="w-5 h-5 text-blue-400" />
                TRANSMISIÓN EN VIVO
              </h3>

              {/* Camera Video */}
              <div className="aspect-video bg-slate-950 rounded-lg mb-3 relative overflow-hidden flex-shrink-0">
                {isStreaming ? (
                  <div className="absolute inset-0">
                    <div className="absolute top-2 left-2 flex items-center gap-2 bg-red-600 px-3 py-1 rounded-full text-xs font-semibold">
                      <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                      EN VIVO
                    </div>
                    <div className="absolute bottom-2 left-2 bg-slate-900/80 backdrop-blur-sm px-3 py-1 rounded text-xs">
                      {cameras.find(c => c.id === selectedCamera)?.name}
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center">
                        <Video className="w-16 h-16 text-slate-700 mx-auto mb-2" />
                        <p className="text-sm text-slate-500">Stream activo...</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Camera className="w-16 h-16 text-slate-700" />
                  </div>
                )}
              </div>

              {/* Camera Selector */}
              <select
                value={selectedCamera}
                onChange={(e) => setSelectedCamera(e.target.value)}
                className="w-full mb-3 px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg focus:outline-none focus:border-blue-500"
              >
                {cameras.map(camera => (
                  <option key={camera.id} value={camera.id}>
                    {camera.name} - {camera.status === 'online' ? '🟢' : '🔴'} {camera.status}
                  </option>
                ))}
              </select>

              {/* Controls */}
              <div className="flex gap-2">
                {!isStreaming ? (
                  <button
                    onClick={() => setIsStreaming(true)}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-green-600 hover:bg-green-700 rounded-lg transition-colors font-semibold"
                  >
                    <Play className="w-5 h-5" />
                    Iniciar
                  </button>
                ) : (
                  <button
                    onClick={() => setIsStreaming(false)}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-red-600 hover:bg-red-700 rounded-lg transition-colors font-semibold"
                  >
                    <Square className="w-5 h-5" />
                    Detener
                  </button>
                )}
              </div>
            </div>

            {/* Alerts Panel */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-4 flex-1 flex flex-col overflow-hidden">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-orange-400" />
                ALERTAS RECIENTES
              </h3>

              <div className="space-y-2 overflow-y-auto flex-1">
                {recentAlerts.map(alert => (
                  <div
                    key={alert.id}
                    className={`p-3 rounded-lg border ${
                      alert.severity === 'danger'
                        ? 'bg-red-900/20 border-red-700/50'
                        : alert.severity === 'warning'
                        ? 'bg-yellow-900/20 border-yellow-700/50'
                        : 'bg-blue-900/20 border-blue-700/50'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <p className="text-sm font-semibold">{alert.message}</p>
                      <span className={`w-2 h-2 rounded-full flex-shrink-0 mt-1 ${
                        alert.severity === 'danger'
                          ? 'bg-red-500'
                          : alert.severity === 'warning'
                          ? 'bg-yellow-500'
                          : 'bg-blue-500'
                      }`}></span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>Zona: {alert.zone}</span>
                      <span>{alert.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Risk Zones Summary */}
            <div className="bg-slate-900 rounded-xl border border-slate-800 p-4">
              <h3 className="font-semibold mb-3">Niveles de Riesgo</h3>
              <div className="space-y-2">
                {riskZones.map(zone => (
                  <div key={zone.id} className="flex items-center justify-between p-2 bg-slate-950 rounded-lg">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${zone.color}`}></div>
                      <span className="text-sm font-medium">{zone.name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-slate-400">{zone.incidents} incidentes</span>
                      <span className={`text-xs px-2 py-1 rounded ${
                        zone.level === 'Alto' ? 'bg-red-500/20 text-red-400' :
                        zone.level === 'Medio' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-green-500/20 text-green-400'
                      }`}>
                        {zone.level}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
