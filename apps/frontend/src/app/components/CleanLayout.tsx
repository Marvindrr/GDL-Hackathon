import { useEffect, useMemo, useRef, useState } from "react";
import { API_ROUTES } from "../config/api";
import { SecurityMap } from "../features/mapa/components/SecurityMap";
import type {
  RutaEscapeMapa,
  ZonaRiesgoMapa,
} from "../features/mapa/types/mapa.types";
import {
  actualizarFiltrosDeteccion,
  obtenerCamaras,
  obtenerEventosCamaras,
  obtenerFiltrosDeteccion,
} from "../services/camaras.service";
import type {
  Camara,
  EventoCamara,
  FiltrosDeteccion,
} from "../types/camaras.types";

import {
  AlertTriangle,
  Bell,
  Circle,
  FileText,
  Home,
  MapPin,
  Monitor,
  Play,
  Route,
  Search,
  Shield,
  Square,
  TrendingUp,
  Video,
} from "lucide-react";

const TIPOS_ROPA_OPTIONS = [
  { value: "cualquiera", label: "Cualquiera" },
  { value: "superior", label: "Ropa superior" },
  { value: "inferior", label: "Ropa inferior" },
] as const;

const COLORES_ROPA_OPTIONS = [
  { value: "cualquiera", label: "Cualquiera" },
  { value: "rojo", label: "Rojo" },
  { value: "naranja", label: "Naranja" },
  { value: "amarillo", label: "Amarillo" },
  { value: "verde", label: "Verde" },
  { value: "azul", label: "Azul" },
  { value: "morado", label: "Morado" },
  { value: "rosa", label: "Rosa" },
  { value: "negro", label: "Negro" },
  { value: "blanco", label: "Blanco" },
  { value: "gris", label: "Gris" },
] as const;

const CONFIANZA_COLOR_OPTIONS = [
  { value: 0.08, label: "Baja - 8%" },
  { value: 0.15, label: "Media - 15%" },
  { value: 0.25, label: "Alta - 25%" },
  { value: 0.35, label: "Muy alta - 35%" },
] as const;

export function CleanLayout() {
  const [activeSection, setActiveSection] = useState("mapa");

  const [calcularRutaTrigger, setCalcularRutaTrigger] = useState(0);
  const [calculandoRutaMapa, setCalculandoRutaMapa] = useState(false);

  const [busquedaMapa, setBusquedaMapa] = useState("");
  const [busquedaMapaTrigger, setBusquedaMapaTrigger] = useState(0);
  const [zonaMapaSeleccionada, setZonaMapaSeleccionada] =
    useState<ZonaRiesgoMapa | null>(null);
  const [rutasEscapeMapa, setRutasEscapeMapa] = useState<RutaEscapeMapa[]>([]);
  const [mensajeBusquedaMapa, setMensajeBusquedaMapa] = useState("");

  const [camaras, setCamaras] = useState<Camara[]>([]);
  const [camaraActualId, setCamaraActualId] = useState("");
  const [streamActivo, setStreamActivo] = useState(false);

  const [historialAlertas, setHistorialAlertas] = useState<EventoCamara[]>([]);
  const [ultimaDeteccion, setUltimaDeteccion] =
    useState<EventoCamara | null>(null);

  const [autoFollow, setAutoFollow] = useState(true);
  const [fijarCamara, setFijarCamara] = useState(false);
  const [errorCamara, setErrorCamara] = useState("");

  const [filtrosDeteccion, setFiltrosDeteccion] =
    useState<FiltrosDeteccion>({
      activo: false,
      tipo_ropa: "cualquiera",
      color_ropa: "cualquiera",
      confianza_color_minima: 0.08,
    });

  const [guardandoFiltros, setGuardandoFiltros] = useState(false);
  const [mostrarFiltroRopa, setMostrarFiltroRopa] = useState(false);

  const ultimaDeteccionKeyRef = useRef("");
  const ultimoCambioAutomaticoRef = useRef(0);

  const COOLDOWN_CAMBIO_MS = 12000;

  const menuItems = [
    { id: "mapa", name: "Mapa Principal", icon: Home },
    { id: "zonas", name: "Zonas de Riesgo", icon: AlertTriangle },
    { id: "graficas", name: "Gráficas", icon: TrendingUp },
    { id: "reportes", name: "Reportes", icon: FileText },
    { id: "camaras", name: "Cámaras", icon: Monitor },
  ];

  const hayCamaras = camaras.length > 0;

  const camaraActual = camaras.find(
    (camara) => camara.id === camaraActualId
  );

  const streamUrl = useMemo(() => {
    if (!camaraActualId || !streamActivo) {
      return "";
    }

    return `${API_ROUTES.streamVivo(camaraActualId)}?t=${Date.now()}`;
  }, [camaraActualId, streamActivo]);

  useEffect(() => {
    cargarCamaras();
    cargarFiltros();
  }, []);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      consultarEventos();
    }, 3000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [camaraActualId, streamActivo, autoFollow, fijarCamara]);

  async function cargarCamaras() {
    try {
      setErrorCamara("");

      const data = await obtenerCamaras();

      setCamaras(data);

      if (data.length > 0) {
        setCamaraActualId(data[0].id);
      } else {
        setCamaraActualId("");
        setStreamActivo(false);
      }
    } catch (error) {
      console.error(error);
      setErrorCamara("No se pudieron cargar las cámaras.");
    }
  }

  async function cargarFiltros() {
    try {
      const filtros = await obtenerFiltrosDeteccion();
      setFiltrosDeteccion(filtros);
    } catch (error) {
      console.error("Error cargando filtros:", error);
    }
  }

  async function guardarFiltros(nuevosFiltros: FiltrosDeteccion) {
    try {
      setGuardandoFiltros(true);

      const filtrosActualizados = await actualizarFiltrosDeteccion(
        nuevosFiltros
      );

      setFiltrosDeteccion(filtrosActualizados);
    } catch (error) {
      console.error("Error guardando filtros:", error);
    } finally {
      setGuardandoFiltros(false);
    }
  }

  function actualizarFiltro<K extends keyof FiltrosDeteccion>(
    key: K,
    value: FiltrosDeteccion[K]
  ) {
    const nuevosFiltros = {
      ...filtrosDeteccion,
      [key]: value,
    };

    setFiltrosDeteccion(nuevosFiltros);
    guardarFiltros(nuevosFiltros);
  }

  async function consultarEventos() {
    try {
      const data = await obtenerEventosCamaras();

      if (!Array.isArray(data) || data.length === 0) {
        return;
      }

      setHistorialAlertas((prev) => {
        const mapaAlertas = new Map<string, EventoCamara>();

        prev.forEach((evento) => {
          mapaAlertas.set(`${evento.camara_id}-${evento.timestamp}`, evento);
        });

        data.forEach((evento) => {
          mapaAlertas.set(`${evento.camara_id}-${evento.timestamp}`, evento);
        });

        return Array.from(mapaAlertas.values())
          .sort((a, b) => b.timestamp - a.timestamp)
          .slice(0, 20);
      });

      const evento = data[0];
      const eventoKey = `${evento.camara_id}-${evento.timestamp}`;

      if (ultimaDeteccionKeyRef.current === eventoKey) {
        return;
      }

      ultimaDeteccionKeyRef.current = eventoKey;
      setUltimaDeteccion(evento);

      if (debeCambiarPorAlerta(evento)) {
        setCamaraActualId(evento.camara_id);
        setStreamActivo(true);
        setActiveSection("camaras");
        ultimoCambioAutomaticoRef.current = Date.now();
      }
    } catch (error) {
      console.error("Error consultando eventos de cámaras:", error);
    }
  }

  function debeCambiarPorAlerta(evento: EventoCamara) {
    if (!autoFollow) return false;
    if (!evento.camara_id) return false;

    if (fijarCamara && evento.camara_id !== camaraActualId) {
      return false;
    }

    if (evento.camara_id === camaraActualId && streamActivo) {
      return false;
    }

    const ahora = Date.now();

    if (ahora - ultimoCambioAutomaticoRef.current < COOLDOWN_CAMBIO_MS) {
      return false;
    }

    return true;
  }

  function iniciarStream() {
    if (!camaraActualId) {
      setErrorCamara("Primero registra una cámara para poder ver el stream.");
      setStreamActivo(false);
      return;
    }

    setErrorCamara("");
    setStreamActivo(true);
    setActiveSection("camaras");
  }

  function detenerStream() {
    setStreamActivo(false);
  }

  function seleccionarAlerta(evento: EventoCamara) {
    setUltimaDeteccion(evento);
    setCamaraActualId(evento.camara_id);
    setStreamActivo(true);
    setActiveSection("camaras");
  }

  function calcularRutaDesdeMapa() {
    if (!zonaMapaSeleccionada) {
      setMensajeBusquedaMapa(
        "Primero busca una colonia o selecciona una zona en el mapa."
      );
      return;
    }

    setCalcularRutaTrigger((prev) => prev + 1);
  }

  function buscarZonaDesdeHeader() {
    setBusquedaMapaTrigger((prev) => prev + 1);
  }

  function formatearDetecciones(evento: EventoCamara | null) {
    if (!evento || !Array.isArray(evento.detecciones)) {
      return "Sin detecciones";
    }

    return evento.detecciones
      .map((item: EventoCamara["detecciones"][number]) => {
        const porcentaje = Math.round((item.confianza || 0) * 100);
        let texto = `${item.clase} ${porcentaje}%`;

        const ropa = item.ropa;

        if (ropa) {
          const superior = ropa.superior?.color || "N/D";
          const inferior = ropa.inferior?.color || "N/D";

          texto += ` | sup: ${superior} | inf: ${inferior}`;
        }

        return texto;
      })
      .join(", ");
  }

  return (
    <div className="w-screen h-screen flex bg-slate-950 text-white overflow-hidden">
      <aside className="w-64 shrink-0 bg-slate-900/50 backdrop-blur-sm border-r border-slate-800/50 flex flex-col">
        <div className="p-6 border-b border-slate-800/50">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-emerald-400" />

            <div>
              <h1 className="text-xl font-bold">SIMPD</h1>
              <p className="text-xs text-slate-400">Guadalajara, México</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;

              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveSection(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    activeSection === item.id
                      ? "bg-emerald-600 text-white shadow-lg"
                      : "text-slate-400 hover:bg-slate-800/50 hover:text-white"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                </button>
              );
            })}

            <button
              type="button"
              onClick={() => {
                window.location.href = API_ROUTES.gdlTurismo;
              }}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-all mt-4"
            >
              <MapPin className="w-5 h-5" />
              <span className="font-medium">GDL Turismo</span>
            </button>
          </div>
        </nav>

        <div className="p-4 border-t border-slate-800/50">
          <div className="bg-slate-900 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-slate-400">
                Estado del Sistema
              </span>
              <Circle className="w-2 h-2 text-emerald-400 fill-emerald-400 animate-pulse" />
            </div>

            <p className="text-sm font-semibold text-emerald-400">
              Activo
            </p>
          </div>
        </div>
      </aside>

      <div className="flex-1 min-w-0 h-screen flex flex-col overflow-hidden">
        <header className="h-[88px] shrink-0 bg-slate-900/50 backdrop-blur-sm border-b border-slate-800/50 px-8 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold">
              Panel de Control -{" "}
              {menuItems.find((item) => item.id === activeSection)?.name}
            </h2>

            <div className="flex items-center gap-6">
              <div className="relative flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />

                  <input
                    type="text"
                    value={busquedaMapa}
                    onChange={(event) => setBusquedaMapa(event.target.value)}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        buscarZonaDesdeHeader();
                      }
                    }}
                    placeholder="Buscar colonia o zona..."
                    className="pl-10 pr-4 py-2 w-80 bg-slate-900 border border-slate-700 rounded-lg text-sm placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>

                <button
                  type="button"
                  onClick={buscarZonaDesdeHeader}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-sm font-semibold transition-colors"
                >
                  Buscar
                </button>
              </div>

              <button
                type="button"
                className="relative p-2 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <Bell className="w-5 h-5" />

                {historialAlertas.length > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                )}
              </button>
            </div>
          </div>
        </header>

        <div className="flex-1 min-h-0 grid grid-cols-2 gap-8 p-8 overflow-y-auto overflow-x-hidden">
          <div className="min-h-[820px] grid grid-rows-[520px_280px] gap-6">
            <div className="min-h-0 flex-1 bg-slate-900 rounded-2xl overflow-hidden relative shadow-2xl border border-slate-800">
              <SecurityMap
                activeSection={activeSection}
                ultimaDeteccion={ultimaDeteccion}
                calcularRutaTrigger={calcularRutaTrigger}
                onCalculandoRutaChange={setCalculandoRutaMapa}
                busquedaZonaTexto={busquedaMapa}
                busquedaZonaTrigger={busquedaMapaTrigger}
                onZonaSeleccionadaChange={setZonaMapaSeleccionada}
                onRutasEscapeChange={setRutasEscapeMapa}
                onMensajeBusquedaChange={setMensajeBusquedaMapa}
              />

              <div className="absolute top-6 right-6 z-[1100]">
                <button
                  type="button"
                  onClick={calcularRutaDesdeMapa}
                  disabled={calculandoRutaMapa}
                  className={`flex items-center gap-2 px-5 py-3 font-semibold rounded-lg shadow-lg transition-all ${
                    calculandoRutaMapa
                      ? "bg-orange-600/50 cursor-not-allowed"
                      : "bg-orange-600 hover:bg-orange-700"
                  }`}
                >
                  <Route
                    className={`w-5 h-5 ${
                      calculandoRutaMapa ? "animate-spin" : ""
                    }`}
                  />

                  {calculandoRutaMapa
                    ? "Calculando..."
                    : "Calcular Ruta de Escape"}
                </button>
              </div>
            </div>

            {activeSection === "camaras" ? (
              <div className="shrink-0 grid grid-cols-2 gap-4">
                <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-semibold">
                      Última detección
                    </h4>

                    {ultimaDeteccion && (
                      <span className="px-2 py-1 rounded-full bg-red-600 text-xs font-bold">
                        Alerta
                      </span>
                    )}
                  </div>

                  {ultimaDeteccion ? (
                    <div className="text-xs text-slate-300 space-y-1">
                      <p>
                        <strong className="text-white">Cámara:</strong>{" "}
                        {ultimaDeteccion.nombre}
                      </p>

                      <p>
                        <strong className="text-white">Zona:</strong>{" "}
                        {ultimaDeteccion.zona || "Sin zona"}
                      </p>

                      <p>
                        <strong className="text-white">Detección:</strong>{" "}
                        {formatearDetecciones(ultimaDeteccion)}
                      </p>

                      <p className="text-slate-500">
                        {new Date(
                          ultimaDeteccion.timestamp * 1000
                        ).toLocaleTimeString()}
                      </p>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-500">
                      Sin detecciones recientes.
                    </p>
                  )}
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-semibold">Últimas alertas</h4>

                    <span className="px-2 py-1 rounded-full bg-red-600 text-xs font-bold">
                      {historialAlertas.length}
                    </span>
                  </div>

                  {historialAlertas.length === 0 ? (
                    <p className="text-xs text-slate-500">
                      Sin alertas recientes.
                    </p>
                  ) : (
                    <div className="space-y-2 max-h-32 overflow-y-auto pr-1">
                      {historialAlertas.slice(0, 8).map((evento) => (
                        <button
                          key={`${evento.camara_id}-${evento.timestamp}`}
                          type="button"
                          onClick={() => seleccionarAlerta(evento)}
                          className="w-full text-left rounded-lg bg-red-500/10 border border-red-500/30 p-2 hover:bg-red-500/20 transition-colors"
                        >
                          <p className="text-xs font-semibold">
                            {evento.nombre}
                          </p>

                          <p className="text-[11px] text-slate-400">
                            {formatearDetecciones(evento)}
                          </p>

                          <p className="text-[10px] text-slate-500 mt-1">
                            {new Date(
                              evento.timestamp * 1000
                            ).toLocaleTimeString()}
                          </p>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="shrink-0 grid grid-cols-[220px_minmax(0,1fr)] gap-4">
                <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
                  <h4 className="text-sm font-semibold mb-3">Niveles de Riesgo</h4>

                  <div className="space-y-2 text-sm text-slate-300">
                    <div className="flex items-center gap-2">
                      <span className="h-3 w-3 rounded-full bg-green-500" />
                      <span>Bajo</span>
                      <span className="text-xs text-slate-500">(0–25)</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="h-3 w-3 rounded-full bg-yellow-500" />
                      <span>Moderado</span>
                      <span className="text-xs text-slate-500">(26–50)</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="h-3 w-3 rounded-full bg-orange-500" />
                      <span>Alto</span>
                      <span className="text-xs text-slate-500">(51–75)</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="h-3 w-3 rounded-full bg-red-500" />
                      <span>Muy alto</span>
                      <span className="text-xs text-slate-500">(76–100)</span>
                    </div>
                  </div>

                  {mensajeBusquedaMapa && (
                    <p className="mt-3 rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-2 text-xs text-yellow-200">
                      {mensajeBusquedaMapa}
                    </p>
                  )}
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 overflow-hidden flex flex-col">
                  <div className="shrink-0 flex items-start justify-between gap-4">
                    <div>
                      <h4 className="text-sm font-semibold">
                        Rutas probables de escape
                      </h4>

                      <p className="mt-1 text-xs text-slate-500">
                        Las rutas e instrucciones se muestran fuera del mapa para no taparlo.
                      </p>
                    </div>

                    {rutasEscapeMapa.length > 0 && (
                      <span className="rounded-full bg-blue-600 px-3 py-1 text-xs font-bold">
                        {rutasEscapeMapa.length} rutas
                      </span>
                    )}
                  </div>

                  <div className="mt-3 min-h-0 flex-1 overflow-y-auto pr-1">
                    {calculandoRutaMapa ? (
                      <div className="rounded-lg border border-orange-500/30 bg-orange-500/10 p-3 text-sm text-orange-200">
                        Calculando rutas probables...
                      </div>
                    ) : rutasEscapeMapa.length === 0 ? (
                      <div className="rounded-lg border border-slate-800 bg-slate-950 p-3 text-sm text-slate-400">
                        Selecciona una colonia en el mapa y presiona “Calcular Ruta de Escape”.
                      </div>
                    ) : (
                      <div className="grid grid-cols-2 gap-3">
                        {rutasEscapeMapa.map((ruta) => (
                          <div
                            key={ruta.id}
                            className="rounded-lg border border-slate-800 bg-slate-950 p-3"
                          >
                            <div className="mb-2 flex items-center justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <span
                                  className="h-3 w-3 rounded-full"
                                  style={{ backgroundColor: ruta.color }}
                                />

                                <p className="text-sm font-semibold text-white">
                                  Ruta {ruta.id}
                                </p>
                              </div>

                              <p className="text-xs text-slate-500">
                                {(ruta.distancia / 1000).toFixed(2)} km
                              </p>
                            </div>

                            <div className="max-h-20 space-y-1 overflow-y-auto pr-1">
                              {ruta.instrucciones.map((instruccion, index) => (
                                <p
                                  key={`${ruta.id}-${index}`}
                                  className="text-xs text-slate-400"
                                >
                                  {index + 1}. {instruccion.texto}
                                </p>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
</div>
            )}
          </div>

          <div className="min-h-[820px] grid grid-rows-[520px_280px] gap-6">
            <div className="min-h-0 flex-1 bg-slate-900 rounded-2xl overflow-hidden relative shadow-2xl border border-slate-800">
              <div className="absolute top-6 left-6 right-6 z-10 flex items-center justify-between">
                <div className="bg-slate-950/80 backdrop-blur-sm px-4 py-2 rounded-lg">
                  <h3 className="font-semibold flex items-center gap-2">
                    <Video className="w-5 h-5 text-emerald-400" />
                    Transmisión en Vivo
                  </h3>
                </div>

                {streamActivo && (
                  <div className="flex items-center gap-2 px-3 py-2 bg-red-600 rounded-lg text-sm font-semibold">
                    <Circle className="w-2 h-2 fill-white animate-pulse" />
                    EN VIVO
                  </div>
                )}
              </div>

              <div className="absolute inset-0 bg-slate-950">
                {streamUrl ? (
                  <img
                    src={streamUrl}
                    alt="Stream en vivo"
                    className="size-full object-cover"
                  />
                ) : (
                  <div className="size-full flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
                    <div className="text-center text-slate-600 px-6">
                      <Video className="w-40 h-40 mx-auto mb-4 opacity-10" />
                      <p className="text-xl font-semibold">Stream detenido</p>
                      <p className="text-sm mt-2">
                        {hayCamaras
                          ? "Selecciona una cámara y presiona Iniciar."
                          : "No hay cámaras configuradas."}
                      </p>
                    </div>
                  </div>
                )}

                {streamActivo && camaraActual && (
                  <div className="absolute bottom-6 left-6 bg-slate-950/80 backdrop-blur-sm px-4 py-2 rounded-lg">
                    <p className="text-sm font-semibold">
                      {camaraActual.nombre}
                    </p>
                    <p className="text-xs text-slate-400">
                      {camaraActual.zona || "Sin zona asignada"}
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="shrink-0 max-h-[340px] overflow-y-auto bg-slate-900 rounded-xl p-5 border border-slate-800">
              <div className="flex gap-3">
                <select
                  value={camaraActualId}
                  disabled={!hayCamaras}
                  onChange={(event) => {
                    setCamaraActualId(event.target.value);
                    setStreamActivo(false);
                    setErrorCamara("");
                  }}
                  className="flex-1 px-4 py-3 bg-slate-950 border border-slate-700 rounded-lg focus:outline-none focus:border-emerald-500 disabled:opacity-50"
                >
                  {!hayCamaras ? (
                    <option value="">No hay cámaras disponibles</option>
                  ) : (
                    camaras.map((camara) => (
                      <option key={camara.id} value={camara.id}>
                        {camara.nombre} {camara.activa ? "●" : "○"}
                      </option>
                    ))
                  )}
                </select>

                {!streamActivo ? (
                  <button
                    type="button"
                    onClick={iniciarStream}
                    disabled={!hayCamaras}
                    className="px-8 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-lg font-semibold flex items-center gap-2 transition-colors"
                  >
                    <Play className="w-5 h-5" />
                    Iniciar
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={detenerStream}
                    className="px-8 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-semibold flex items-center gap-2 transition-colors"
                  >
                    <Square className="w-5 h-5" />
                    Detener
                  </button>
                )}
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-slate-400">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={autoFollow}
                    onChange={(event) => setAutoFollow(event.target.checked)}
                  />
                  Cambiar con alerta
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={fijarCamara}
                    onChange={(event) => setFijarCamara(event.target.checked)}
                  />
                  Fijar cámara
                </label>
              </div>

              {errorCamara && (
                <p className="mt-3 text-sm text-red-400">{errorCamara}</p>
              )}

              <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950/70">
                <div className="flex items-center justify-between px-4 py-3">
                  <div>
                    <h4 className="text-sm font-semibold">Filtro por ropa</h4>
                    <p className="text-xs text-slate-500 mt-1">
                      {filtrosDeteccion.activo
                        ? `${filtrosDeteccion.tipo_ropa} • ${filtrosDeteccion.color_ropa}`
                        : "Filtro apagado"}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <label className="flex items-center gap-2 text-xs text-slate-400">
                      <input
                        type="checkbox"
                        checked={filtrosDeteccion.activo}
                        onChange={(event) =>
                          actualizarFiltro("activo", event.target.checked)
                        }
                      />
                      Activo
                    </label>

                    <button
                      type="button"
                      onClick={() => setMostrarFiltroRopa((prev) => !prev)}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold transition-colors"
                    >
                      {mostrarFiltroRopa ? "Ocultar" : "Mostrar"}
                    </button>
                  </div>
                </div>

                {mostrarFiltroRopa && (
                  <div className="border-t border-slate-800 px-4 py-4">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-slate-500 mb-1">
                          Tipo
                        </label>
                        <select
                          value={filtrosDeteccion.tipo_ropa}
                          onChange={(event) =>
                            actualizarFiltro(
                              "tipo_ropa",
                              event.target
                                .value as FiltrosDeteccion["tipo_ropa"]
                            )
                          }
                          className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm focus:outline-none focus:border-emerald-500"
                        >
                          {TIPOS_ROPA_OPTIONS.map((tipo) => (
                            <option key={tipo.value} value={tipo.value}>
                              {tipo.label}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs text-slate-500 mb-1">
                          Color
                        </label>
                        <select
                          value={filtrosDeteccion.color_ropa}
                          onChange={(event) =>
                            actualizarFiltro(
                              "color_ropa",
                              event.target
                                .value as FiltrosDeteccion["color_ropa"]
                            )
                          }
                          className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm focus:outline-none focus:border-emerald-500"
                        >
                          {COLORES_ROPA_OPTIONS.map((color) => (
                            <option key={color.value} value={color.value}>
                              {color.label}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    <div className="mt-3">
                      <label className="block text-xs text-slate-500 mb-1">
                        Confianza mínima de color
                      </label>
                      <select
                        value={String(filtrosDeteccion.confianza_color_minima)}
                        onChange={(event) =>
                          actualizarFiltro(
                            "confianza_color_minima",
                            Number(event.target.value)
                          )
                        }
                        className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm focus:outline-none focus:border-emerald-500"
                      >
                        {CONFIANZA_COLOR_OPTIONS.map((opcion) => (
                          <option key={opcion.value} value={opcion.value}>
                            {opcion.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <p className="mt-3 text-xs text-slate-500">
                      {guardandoFiltros
                        ? "Guardando filtros..."
                        : filtrosDeteccion.activo
                        ? `Buscando ${filtrosDeteccion.tipo_ropa} color ${filtrosDeteccion.color_ropa}.`
                        : "Filtro apagado. Se alertará por cualquier detección configurada."}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}