import { useEffect, useMemo, useRef, useState } from "react";
import {
  obtenerCamaras,
  obtenerEventosCamaras,
} from "../services/camaras.service";
import { API_ROUTES } from "../config/api";
import type { Camara, EventoCamara } from "../types/camaras.types";

export function CameraPanel() {
  const [camaras, setCamaras] = useState<Camara[]>([]);
  const [camaraActualId, setCamaraActualId] = useState<string>("");
  const [streamActivo, setStreamActivo] = useState(false);
  const [eventos, setEventos] = useState<EventoCamara[]>([]);
  const [historialAlertas, setHistorialAlertas] = useState<EventoCamara[]>([]);
  const [ultimaDeteccion, setUltimaDeteccion] =
    useState<EventoCamara | null>(null);
  const [autoFollow, setAutoFollow] = useState(true);
  const [fijarCamara, setFijarCamara] = useState(false);
  const [error, setError] = useState<string>("");

  const ultimaDeteccionKeyRef = useRef("");
  const ultimoCambioAutomaticoRef = useRef(0);

  const COOLDOWN_CAMBIO_MS = 12000;

  useEffect(() => {
    cargarCamaras();
  }, []);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      consultarEventos();
    }, 3000);

    return () => {
      window.clearInterval(intervalId);
    };
  }, [camaraActualId, autoFollow, fijarCamara]);

  async function cargarCamaras() {
    try {
      setError("");

      const data = await obtenerCamaras();

      setCamaras(data);

      if (data.length > 0) {
        setCamaraActualId(data[0].id);
      }
    } catch (error) {
      console.error(error);
      setError("No se pudieron cargar las cámaras.");
    }
  }

  async function consultarEventos() {
    try {
      const data = await obtenerEventosCamaras();

      setEventos(data);

      if (!Array.isArray(data) || data.length === 0) {
        return;
      }

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
        ultimoCambioAutomaticoRef.current = Date.now();
      }
    } catch (error) {
      console.error("Error consultando eventos de cámaras:", error);
    }
  }

  function debeCambiarPorAlerta(evento: EventoCamara) {
    if (!autoFollow) return false;
    if (fijarCamara) return false;
    if (!evento.camara_id) return false;
    if (evento.camara_id === camaraActualId) return false;

    const ahora = Date.now();

    if (ahora - ultimoCambioAutomaticoRef.current < COOLDOWN_CAMBIO_MS) {
      return false;
    }

    return true;
  }

  function iniciarStream() {
    if (!camaraActualId) {
      setError("Selecciona una cámara para iniciar el stream.");
      return;
    }

    setError("");
    setStreamActivo(true);
  }

  function detenerStream() {
    setStreamActivo(false);
  }

  function seleccionarEvento(evento: EventoCamara) {
    setUltimaDeteccion(evento);
    setCamaraActualId(evento.camara_id);
    setStreamActivo(true);
  }

  function formatearDetecciones(evento: EventoCamara | null) {
    if (!evento || !Array.isArray(evento.detecciones)) {
      return "Sin detecciones";
    }

    return evento.detecciones
      .map((item) => {
        const porcentaje = Math.round((item.confianza || 0) * 100);
        return `${item.clase} ${porcentaje}%`;
      })
      .join(", ");
  }

  const streamUrl = useMemo(() => {
    if (!camaraActualId || !streamActivo) {
      return "";
    }

    return `${API_ROUTES.streamVivo(camaraActualId)}?t=${Date.now()}`;
  }, [camaraActualId, streamActivo]);

  const camaraActual = camaras.find((camara) => camara.id === camaraActualId);

  return (
    <aside className="h-full bg-slate-950 text-white border-l border-white/10 flex flex-col overflow-hidden">
      <section className="p-4 border-b border-white/10">
        <div className="flex items-start justify-between gap-3 mb-4">
          <div>
            <h2 className="text-lg font-extrabold">Stream en vivo</h2>
            <p className="text-sm text-slate-400">
              {camaraActual
                ? camaraActual.nombre
                : "No hay cámara seleccionada"}
            </p>
          </div>

          <span
            className={`px-3 py-1 rounded-full text-xs font-bold ${
              streamActivo ? "bg-green-600" : "bg-slate-700"
            }`}
          >
            {streamActivo ? "Activo" : "Inactivo"}
          </span>
        </div>

        <select
          value={camaraActualId}
          onChange={(event) => {
            setCamaraActualId(event.target.value);
            setStreamActivo(false);
          }}
          className="w-full h-10 rounded-xl px-3 text-slate-900 font-semibold outline-none"
        >
          {camaras.length === 0 ? (
            <option value="">No hay cámaras disponibles</option>
          ) : (
            camaras.map((camara) => (
              <option key={camara.id} value={camara.id}>
                {camara.nombre}
              </option>
            ))
          )}
        </select>

        <div className="grid grid-cols-2 gap-2 mt-3">
          <button
            type="button"
            onClick={iniciarStream}
            className="h-10 rounded-xl bg-green-600 hover:bg-green-700 font-bold transition"
          >
            Ver en vivo
          </button>

          <button
            type="button"
            onClick={detenerStream}
            className="h-10 rounded-xl bg-red-600 hover:bg-red-700 font-bold transition"
          >
            Detener
          </button>
        </div>

        <label className="flex items-center gap-2 mt-4 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={autoFollow}
            onChange={(event) => setAutoFollow(event.target.checked)}
          />
          Cambiar automáticamente a cámara con alerta
        </label>

        <label className="flex items-center gap-2 mt-2 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={fijarCamara}
            onChange={(event) => setFijarCamara(event.target.checked)}
          />
          Fijar cámara actual
        </label>

        {error && (
          <p className="mt-3 text-sm text-red-400">
            {error}
          </p>
        )}
      </section>

      <section className="bg-black h-[260px] flex items-center justify-center">
        {streamUrl ? (
          <img
            src={streamUrl}
            alt="Stream en vivo"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-center px-6">
            <strong className="block text-white">
              Stream detenido
            </strong>
            <span className="text-sm text-slate-400">
              Selecciona una cámara y presiona “Ver en vivo”.
            </span>
          </div>
        )}
      </section>

      <section className="p-4 border-b border-white/10">
        <div className="flex items-center justify-between gap-2 mb-3">
          <h3 className="font-bold">Última detección</h3>

          {ultimaDeteccion && (
            <span className="text-xs bg-red-600 px-2 py-1 rounded-full font-bold">
              Alerta
            </span>
          )}
        </div>

        {ultimaDeteccion ? (
          <div className="rounded-2xl bg-white/10 p-3 text-sm space-y-1">
            <p>
              <strong>Cámara:</strong> {ultimaDeteccion.nombre}
            </p>

            <p>
              <strong>Zona:</strong>{" "}
              {ultimaDeteccion.zona || "Sin zona"}
            </p>

            <p>
              <strong>Detección:</strong>{" "}
              {formatearDetecciones(ultimaDeteccion)}
            </p>

            <p className="text-slate-400 text-xs">
              {new Date(
                ultimaDeteccion.timestamp * 1000
              ).toLocaleTimeString()}
            </p>
          </div>
        ) : (
          <p className="text-sm text-slate-400">
            Sin detecciones recientes.
          </p>
        )}
      </section>

      <section className="p-4 overflow-y-auto flex-1">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-bold">Últimas alertas</h3>

          <span className="bg-red-600 text-white rounded-full px-2 py-1 text-xs font-bold">
            {eventos.length}
          </span>
        </div>

        <div className="flex flex-col gap-2">
          {eventos.length === 0 ? (
            <p className="text-sm text-slate-400">
              Sin alertas recientes.
            </p>
          ) : (
            eventos.slice(0, 6).map((evento) => (
              <button
                key={`${evento.camara_id}-${evento.timestamp}`}
                type="button"
                onClick={() => seleccionarEvento(evento)}
                className="text-left rounded-2xl bg-red-500/10 border border-red-500/30 p-3 hover:bg-red-500/20 transition"
              >
                <strong className="block text-sm">
                  {evento.nombre}
                </strong>

                <span className="block text-xs text-slate-300">
                  {formatearDetecciones(evento)}
                </span>

                <span className="block text-xs text-slate-400 mt-1">
                  {new Date(evento.timestamp * 1000).toLocaleTimeString()}
                </span>
              </button>
            ))
          )}
        </div>
      </section>
    </aside>
  );
}