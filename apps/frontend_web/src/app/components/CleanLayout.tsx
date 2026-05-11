import { useState } from 'react';
import {
  Shield,
  MapPin,
  Video,
  AlertTriangle,
  Search,
  Play,
  Square,
  Bell,
  Camera,
  Navigation,
  X,
  Circle,
  TrendingUp,
  FileText,
  Monitor,
  Home,
  Route
} from 'lucide-react';

export function CleanLayout() {
  const [selectedCamera, setSelectedCamera] = useState('cam-001');
  const [isStreaming, setIsStreaming] = useState(true);
  const [showEscapeAlert, setShowEscapeAlert] = useState(true);
  const [activeSection, setActiveSection] = useState('mapa');
  const [calculatingRoute, setCalculatingRoute] = useState(false);

  const cameras = [
    { id: 'cam-001', name: 'Entrada Principal', status: 'online' },
    { id: 'cam-002', name: 'Estacionamiento A', status: 'online' },
    { id: 'cam-003', name: 'Perímetro Norte', status: 'online' },
    { id: 'cam-004', name: 'Salida Sur', status: 'offline' },
  ];

  const riskZones = [
    { name: 'Centro', level: 'Alto', color: 'bg-red-500' },
    { name: 'Norte', level: 'Medio', color: 'bg-yellow-500' },
    { name: 'Sur', level: 'Bajo', color: 'bg-green-500' },
  ];

  const menuItems = [
    { id: 'mapa', name: 'Mapa Principal', icon: Home },
    { id: 'zonas', name: 'Zonas de Riesgo', icon: AlertTriangle },
    { id: 'graficas', name: 'Gráficas', icon: TrendingUp },
    { id: 'reportes', name: 'Reportes', icon: FileText },
    { id: 'camaras', name: 'Cámaras', icon: Monitor },
  ];

  const handleCalculateRoute = () => {
    setCalculatingRoute(true);
    setShowEscapeAlert(true);
    setTimeout(() => {
      setCalculatingRoute(false);
    }, 2000);
  };

  return (
    <div className="size-full flex bg-slate-950 text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900/50 backdrop-blur-sm border-r border-slate-800/50 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-slate-800/50">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-emerald-400" />
            <div>
              <h1 className="text-xl font-bold">SecureVision</h1>
              <p className="text-xs text-slate-400">Guadalajara, México</p>
            </div>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {menuItems.map(item => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveSection(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    activeSection === item.id
                      ? 'bg-emerald-600 text-white shadow-lg'
                      : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                </button>
              );
            })}
          </div>
        </nav>

        {/* System Status */}
        <div className="p-4 border-t border-slate-800/50">
          <div className="bg-slate-900 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">Estado del Sistema</span>
              <Circle className="w-2 h-2 text-emerald-400 fill-emerald-400 animate-pulse" />
            </div>
            <p className="text-sm font-semibold text-emerald-400">Operacional</p>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-800/50 px-8 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold">Panel de Control - {menuItems.find(m => m.id === activeSection)?.name}</h2>

            <div className="flex items-center gap-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  placeholder="Buscar zona o cámara..."
                  className="pl-10 pr-4 py-2 w-80 bg-slate-900 border border-slate-700 rounded-lg text-sm placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <button className="relative p-2 hover:bg-slate-800 rounded-lg transition-colors">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
            </div>
          </div>
        </header>

        {/* Main Content - Split 50/50 */}
        <div className="flex-1 grid grid-cols-2 gap-8 p-8 overflow-hidden">
          {/* LEFT SIDE - MAP (50%) */}
          <div className="flex flex-col gap-6">
            {/* Large Map */}
            <div className="flex-1 bg-slate-900 rounded-2xl overflow-hidden relative shadow-2xl border border-slate-800">
              {/* Map Header */}
              <div className="absolute top-6 left-6 z-10 bg-slate-950/80 backdrop-blur-sm px-4 py-2 rounded-lg">
                <h3 className="font-semibold flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-emerald-400" />
                  Mapa de Seguridad
                </h3>
              </div>

              {/* Calculate Route Button */}
              <div className="absolute top-6 right-6 z-10">
                <button
                  onClick={handleCalculateRoute}
                  disabled={calculatingRoute}
                  className={`flex items-center gap-2 px-5 py-3 font-semibold rounded-lg shadow-lg transition-all ${
                    calculatingRoute
                      ? 'bg-orange-600/50 cursor-not-allowed'
                      : 'bg-orange-600 hover:bg-orange-700'
                  }`}
                >
                  <Route className={`w-5 h-5 ${calculatingRoute ? 'animate-spin' : ''}`} />
                  {calculatingRoute ? 'Calculando...' : 'Calcular Ruta de Escape'}
                </button>
              </div>

              {/* Map Display Area */}
              <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
                <div className="text-center text-slate-600">
                  <MapPin className="w-40 h-40 mx-auto mb-4 opacity-10" />
                  <p className="text-xl font-semibold">Área de Monitoreo</p>
                  <p className="text-sm mt-2">Guadalajara - Zona Metropolitana</p>
                </div>
              </div>

              {/* Risk Zone Pins */}
              <div className="absolute top-1/3 left-1/4">
                <div className="w-10 h-10 bg-red-500 rounded-full animate-pulse shadow-xl shadow-red-500/50 cursor-pointer"></div>
                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 bg-slate-950 px-3 py-1 rounded-lg whitespace-nowrap text-xs">
                  Centro - Alto
                </div>
              </div>

              <div className="absolute top-1/2 right-1/3">
                <div className="w-8 h-8 bg-yellow-500 rounded-full animate-pulse shadow-xl shadow-yellow-500/50 cursor-pointer"></div>
                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 bg-slate-950 px-3 py-1 rounded-lg whitespace-nowrap text-xs">
                  Norte - Medio
                </div>
              </div>

              <div className="absolute bottom-1/4 left-1/2">
                <div className="w-7 h-7 bg-green-500 rounded-full animate-pulse shadow-xl shadow-green-500/50 cursor-pointer"></div>
                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 bg-slate-950 px-3 py-1 rounded-lg whitespace-nowrap text-xs">
                  Sur - Bajo
                </div>
              </div>

              {/* Escape Route Path - shown when calculating or alert active */}
              {(calculatingRoute || showEscapeAlert) && (
                <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 5 }}>
                  <defs>
                    <marker
                      id="arrowhead"
                      markerWidth="10"
                      markerHeight="10"
                      refX="9"
                      refY="3"
                      orient="auto"
                    >
                      <polygon points="0 0, 10 3, 0 6" fill="#f97316" />
                    </marker>
                  </defs>
                  <path
                    d="M 25% 33% L 35% 25% L 50% 20% L 65% 15% L 80% 10%"
                    stroke="#f97316"
                    strokeWidth="3"
                    fill="none"
                    strokeDasharray="10,5"
                    markerEnd="url(#arrowhead)"
                    className={calculatingRoute ? 'animate-pulse' : ''}
                  />
                </svg>
              )}

              {/* Map Controls */}
              <div className="absolute bottom-6 right-6 flex gap-2">
                <button className="p-3 bg-slate-950/80 backdrop-blur-sm hover:bg-slate-900 rounded-lg transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </button>
                <button className="p-3 bg-slate-950/80 backdrop-blur-sm hover:bg-slate-900 rounded-lg transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Risk Zones Info */}
            <div className="bg-slate-900 rounded-xl p-5 border border-slate-800">
              <h4 className="font-semibold mb-3 text-sm">Niveles de Riesgo</h4>
              <div className="flex gap-4">
                {riskZones.map(zone => (
                  <div key={zone.name} className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${zone.color}`}></div>
                    <span className="text-sm">{zone.name}</span>
                    <span className="text-xs text-slate-500">({zone.level})</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT SIDE - CAMERA (50%) */}
          <div className="flex flex-col gap-6">
            {/* Large Camera Feed */}
            <div className="flex-1 bg-slate-900 rounded-2xl overflow-hidden relative shadow-2xl border border-slate-800">
              {/* Camera Header */}
              <div className="absolute top-6 left-6 right-6 z-10 flex items-center justify-between">
                <div className="bg-slate-950/80 backdrop-blur-sm px-4 py-2 rounded-lg">
                  <h3 className="font-semibold flex items-center gap-2">
                    <Video className="w-5 h-5 text-emerald-400" />
                    Transmisión en Vivo
                  </h3>
                </div>

                {isStreaming && (
                  <div className="flex items-center gap-2 px-3 py-2 bg-red-600 rounded-lg text-sm font-semibold">
                    <Circle className="w-2 h-2 fill-white animate-pulse" />
                    EN VIVO
                  </div>
                )}
              </div>

              {/* Camera Display Area */}
              <div className="absolute inset-0 bg-slate-950">
                {isStreaming ? (
                  <div className="size-full flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
                    <div className="text-center text-slate-600">
                      <Video className="w-40 h-40 mx-auto mb-4 opacity-10" />
                      <p className="text-xl font-semibold">Stream Activo</p>
                      <p className="text-sm mt-2">{cameras.find(c => c.id === selectedCamera)?.name}</p>
                    </div>
                  </div>
                ) : (
                  <div className="size-full flex items-center justify-center">
                    <Camera className="w-40 h-40 text-slate-800" />
                  </div>
                )}

                {/* Camera Info Overlay */}
                {isStreaming && (
                  <div className="absolute bottom-6 left-6 bg-slate-950/80 backdrop-blur-sm px-4 py-2 rounded-lg">
                    <p className="text-sm font-semibold">{cameras.find(c => c.id === selectedCamera)?.name}</p>
                    <p className="text-xs text-slate-400">1920x1080 • 30fps</p>
                  </div>
                )}
              </div>
            </div>

            {/* Camera Controls */}
            <div className="bg-slate-900 rounded-xl p-5 border border-slate-800">
              <div className="flex gap-3">
                <select
                  value={selectedCamera}
                  onChange={(e) => setSelectedCamera(e.target.value)}
                  className="flex-1 px-4 py-3 bg-slate-950 border border-slate-700 rounded-lg focus:outline-none focus:border-emerald-500"
                >
                  {cameras.map(camera => (
                    <option key={camera.id} value={camera.id}>
                      {camera.name} {camera.status === 'online' ? '●' : '○'}
                    </option>
                  ))}
                </select>

                {!isStreaming ? (
                  <button
                    onClick={() => setIsStreaming(true)}
                    className="px-8 py-3 bg-emerald-600 hover:bg-emerald-700 rounded-lg font-semibold flex items-center gap-2 transition-colors"
                  >
                    <Play className="w-5 h-5" />
                    Iniciar
                  </button>
                ) : (
                  <button
                    onClick={() => setIsStreaming(false)}
                    className="px-8 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-semibold flex items-center gap-2 transition-colors"
                  >
                    <Square className="w-5 h-5" />
                    Detener
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Escape Route Alert - Bottom */}
        {showEscapeAlert && (
          <div className="mx-8 mb-8">
            <div className="bg-gradient-to-r from-orange-600 to-red-600 rounded-xl p-5 shadow-2xl relative">
              <button
                onClick={() => setShowEscapeAlert(false)}
                className="absolute top-4 right-4 p-1 hover:bg-white/20 rounded transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
              <div className="flex items-center gap-4">
                <Navigation className="w-10 h-10 animate-pulse" />
                <div className="flex-1">
                  <h3 className="font-bold text-xl mb-1">RUTA DE EVACUACIÓN ACTIVADA</h3>
                  <p className="text-sm opacity-90">
                    Dirigirse a la <strong>Salida Norte</strong> • Distancia: 150 metros • Tiempo estimado: 2 minutos • Evitar Zona Centro
                  </p>
                </div>
                <button className="px-6 py-3 bg-white text-red-600 font-bold rounded-lg hover:bg-slate-100 transition-colors">
                  Ver Instrucciones
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
