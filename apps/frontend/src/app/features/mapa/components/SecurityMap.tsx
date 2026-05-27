import { Fragment, useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet-routing-machine";
import {
  Circle,
  CircleMarker,
  MapContainer,
  Marker,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";

import type { EventoCamara } from "../../../types/camaras.types";
import {
  buscarZonaMapa,
  obtenerCamarasMapa,
  obtenerZonasMapa,
} from "../services/mapa.service";
import type {
  MapaCamara,
  PuntoMapa,
  RutaEscapeMapa,
  ZonaRiesgoMapa,
} from "../types/mapa.types";

type Props = {
  activeSection: string;
  ultimaDeteccion: EventoCamara | null;
  calcularRutaTrigger?: number;
  onCalculandoRutaChange?: (loading: boolean) => void;
  busquedaZonaTexto?: string;
  busquedaZonaTrigger?: number;
  onZonaSeleccionadaChange?: (zona: ZonaRiesgoMapa | null) => void;
  onRutasEscapeChange?: (rutas: RutaEscapeMapa[]) => void;
  onMensajeBusquedaChange?: (mensaje: string) => void;
};

const GDL_CENTER: [number, number] = [20.6736, -103.344];

const COLORES_RUTA = ["#00b894", "#d63031", "#0984e3", "#e17055"];

const cameraIcon = L.divIcon({
  className: "",
  html: `
    <div style="
      width: 28px;
      height: 28px;
      border-radius: 999px;
      background: #059669;
      border: 3px solid white;
      box-shadow: 0 8px 20px rgba(0,0,0,.45);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: bold;
      font-size: 12px;
    ">
      C
    </div>
  `,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
});

const alertCameraIcon = L.divIcon({
  className: "",
  html: `
    <div style="
      width: 34px;
      height: 34px;
      border-radius: 999px;
      background: #dc2626;
      border: 3px solid white;
      box-shadow: 0 0 0 8px rgba(220,38,38,.25), 0 8px 20px rgba(0,0,0,.45);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: bold;
      font-size: 12px;
    ">
      !
    </div>
  `,
  iconSize: [34, 34],
  iconAnchor: [17, 17],
});

function colorPorRiesgoValor(riesgo: number) {
  if (riesgo <= 25) return "#22c55e";
  if (riesgo <= 50) return "#eab308";
  if (riesgo <= 75) return "#f97316";

  return "#ef4444";
}

function radioPorRiesgo(riesgo: number) {
  if (riesgo >= 76) return 550;
  if (riesgo >= 51) return 450;
  if (riesgo >= 26) return 350;

  return 250;
}

function textoNivelRiesgo(riesgo: number) {
  if (riesgo <= 25) return "Bajo";
  if (riesgo <= 50) return "Moderado";
  if (riesgo <= 75) return "Alto";

  return "Muy alto";
}

function MapController({
  selectedPoint,
}: {
  selectedPoint: PuntoMapa | null;
}) {
  const map = useMap();

  useEffect(() => {
    if (!selectedPoint) {
      return;
    }

    map.setView([selectedPoint.lat, selectedPoint.lng], 15);
  }, [map, selectedPoint]);

  return null;
}

function RoutingController({
  origen,
  calcularRutaTrigger,
  onCalculandoRutaChange,
  onRutasEscapeChange,
}: {
  origen: PuntoMapa | null;
  calcularRutaTrigger: number;
  onCalculandoRutaChange?: (loading: boolean) => void;
  onRutasEscapeChange?: (rutas: RutaEscapeMapa[]) => void;
}) {
  const map = useMap();
  const routeControlsRef = useRef<any[]>([]);

  function limpiarRutas() {
    routeControlsRef.current.forEach((control) => {
      try {
        map.removeControl(control);
      } catch {
        // Ignorar si el control ya fue removido.
      }
    });

    routeControlsRef.current = [];
  }

  useEffect(() => {
    return () => {
      limpiarRutas();
    };
  }, []);

  useEffect(() => {
    limpiarRutas();
    onRutasEscapeChange?.([]);
    onCalculandoRutaChange?.(false);
  }, [origen?.lat, origen?.lng]);

  useEffect(() => {
    if (calcularRutaTrigger <= 0 || !origen) {
      return;
    }

    limpiarRutas();
    onRutasEscapeChange?.([]);
    onCalculandoRutaChange?.(true);

    const destinos = [
      { lat: origen.lat + 0.01, lng: origen.lng + 0.01 },
      { lat: origen.lat - 0.01, lng: origen.lng - 0.01 },
      { lat: origen.lat + 0.01, lng: origen.lng - 0.01 },
      { lat: origen.lat - 0.01, lng: origen.lng + 0.01 },
    ];

    let rutasTerminadas = 0;
    const rutasResultado: RutaEscapeMapa[] = [];

    destinos.forEach((destino, index) => {
      const color = COLORES_RUTA[index % COLORES_RUTA.length];

      const control = (L as any).Routing.control({
        waypoints: [
          L.latLng(origen.lat, origen.lng),
          L.latLng(destino.lat, destino.lng),
        ],
        addWaypoints: false,
        draggableWaypoints: false,
        fitSelectedRoutes: index === 0,
        show: false,
        createMarker: () => null,
        lineOptions: {
          styles: [
            {
              color,
              weight: 5,
              opacity: 0.85,
            },
          ],
        },
      }).addTo(map);

      routeControlsRef.current.push(control);

      const container = control.getContainer?.();

      if (container) {
        container.style.display = "none";
      }

      control.on("routesfound", (event: any) => {
        const route = event.routes?.[0];

        if (route) {
          rutasResultado.push({
            id: index + 1,
            color,
            distancia: route.summary?.totalDistance || 0,
            duracion: route.summary?.totalTime || 0,
            instrucciones: (route.instructions || []).map(
              (instruction: any) => ({
                texto: instruction.text,
              })
            ),
          });
        }

        rutasTerminadas += 1;

        if (rutasTerminadas === destinos.length) {
          rutasResultado.sort((a, b) => a.id - b.id);
          onRutasEscapeChange?.(rutasResultado);
          onCalculandoRutaChange?.(false);
        }
      });

      control.on("routingerror", () => {
        rutasTerminadas += 1;

        if (rutasTerminadas === destinos.length) {
          rutasResultado.sort((a, b) => a.id - b.id);
          onRutasEscapeChange?.(rutasResultado);
          onCalculandoRutaChange?.(false);
        }
      });
    });
  }, [calcularRutaTrigger]);

  return null;
}

export function SecurityMap({
  ultimaDeteccion,
  calcularRutaTrigger = 0,
  onCalculandoRutaChange,
  busquedaZonaTexto = "",
  busquedaZonaTrigger = 0,
  onZonaSeleccionadaChange,
  onRutasEscapeChange,
  onMensajeBusquedaChange,
}: Props) {
  const [zonas, setZonas] = useState<ZonaRiesgoMapa[]>([]);
  const [camaras, setCamaras] = useState<MapaCamara[]>([]);
  const [selectedPoint, setSelectedPoint] = useState<PuntoMapa | null>(null);
  const [zonaSeleccionada, setZonaSeleccionada] =
    useState<ZonaRiesgoMapa | null>(null);

  useEffect(() => {
    cargarDatosMapa();
  }, []);

  useEffect(() => {
    if (busquedaZonaTrigger <= 0) {
      return;
    }

    buscarZonaDesdeBackend(busquedaZonaTexto);
  }, [busquedaZonaTrigger]);

  useEffect(() => {
    if (!ultimaDeteccion?.latitud || !ultimaDeteccion?.longitud) {
      return;
    }

    setSelectedPoint({
      lat: ultimaDeteccion.latitud,
      lng: ultimaDeteccion.longitud,
    });
  }, [ultimaDeteccion]);

  async function cargarDatosMapa() {
    try {
      const [zonasData, camarasData] = await Promise.all([
        obtenerZonasMapa(),
        obtenerCamarasMapa(),
      ]);

      setZonas(zonasData);
      setCamaras(camarasData);
    } catch (error) {
      console.error("Error cargando mapa:", error);
      onMensajeBusquedaChange?.("Error cargando las zonas del mapa.");
    }
  }

  function seleccionarZona(zona: ZonaRiesgoMapa) {
    const punto = {
      lat: zona.latitud,
      lng: zona.longitud,
    };

    setZonaSeleccionada(zona);
    setSelectedPoint(punto);

    onZonaSeleccionadaChange?.(zona);
    onRutasEscapeChange?.([]);
    onMensajeBusquedaChange?.("");
  }

  async function buscarZonaDesdeBackend(texto: string) {
    const query = texto.trim();

    if (!query) {
      onMensajeBusquedaChange?.("Escribe el nombre de una colonia.");
      return;
    }

    try {
      const zona = await buscarZonaMapa(query);

      if (!zona) {
        onMensajeBusquedaChange?.(`No se encontró una colonia con: ${query}`);
        return;
      }

      seleccionarZona(zona);
    } catch (error) {
      console.error("Error buscando zona:", error);
      onMensajeBusquedaChange?.("Error buscando la colonia.");
    }
  }

  return (
    <div className="absolute inset-0 bg-slate-950">
      <MapContainer
        center={GDL_CENTER}
        zoom={12}
        scrollWheelZoom
        className="h-full w-full"
      >
        <TileLayer
          attribution="&copy; OpenStreetMap"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {zonas.map((zona) => {
          const selected = zonaSeleccionada?.id === zona.id;
          const color = colorPorRiesgoValor(zona.riesgo);
          const radio = zona.radio || radioPorRiesgo(zona.riesgo);

          return (
            <Fragment key={zona.id}>
              <Circle
                center={[zona.latitud, zona.longitud]}
                radius={radio}
                pathOptions={{
                  color,
                  fillColor: color,
                  fillOpacity: selected ? 0.45 : 0.16,
                  weight: selected ? 5 : 1.5,
                }}
                eventHandlers={{
                  click: () => seleccionarZona(zona),
                }}
              >
                <Popup>
                  <div style={{ minWidth: 160 }}>
                    <strong>{zona.nombre}</strong>
                    <br />
                    Riesgo detectado: <strong>{zona.riesgo}%</strong>
                    <br />
                    Nivel: <strong>{textoNivelRiesgo(zona.riesgo)}</strong>
                  </div>
                </Popup>
              </Circle>

              <CircleMarker
                center={[zona.latitud, zona.longitud]}
                radius={selected ? 8 : 6}
                pathOptions={{
                  color: "#ffffff",
                  weight: 2,
                  fillColor: color,
                  fillOpacity: 1,
                }}
                eventHandlers={{
                  click: () => seleccionarZona(zona),
                }}
              >
                <Popup>
                  <div style={{ minWidth: 160 }}>
                    <strong>{zona.nombre}</strong>
                    <br />
                    Riesgo detectado: <strong>{zona.riesgo}%</strong>
                    <br />
                    Nivel: <strong>{textoNivelRiesgo(zona.riesgo)}</strong>
                  </div>
                </Popup>
              </CircleMarker>
            </Fragment>
          );
        })}

        {camaras.map((camara) => {
          const esAlerta = ultimaDeteccion?.camara_id === camara.id;

          return (
            <Marker
              key={camara.id}
              position={[camara.latitud, camara.longitud]}
              icon={esAlerta ? alertCameraIcon : cameraIcon}
              eventHandlers={{
                click: () => {
                  setSelectedPoint({
                    lat: camara.latitud,
                    lng: camara.longitud,
                  });
                },
              }}
            >
              <Popup>
                <strong>{camara.nombre}</strong>
                <br />
                {camara.zona || "Sin zona"}
                <br />
                {camara.activa ? "Activa" : "Inactiva"}
              </Popup>
            </Marker>
          );
        })}

        <MapController selectedPoint={selectedPoint} />

        <RoutingController
          origen={selectedPoint}
          calcularRutaTrigger={calcularRutaTrigger}
          onCalculandoRutaChange={onCalculandoRutaChange}
          onRutasEscapeChange={onRutasEscapeChange}
        />
      </MapContainer>
    </div>
  );
}