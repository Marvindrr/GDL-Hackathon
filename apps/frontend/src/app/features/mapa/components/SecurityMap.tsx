import { Fragment, useEffect, useState } from "react";
import L from "leaflet";
import {
  Circle,
  CircleMarker,
  MapContainer,
  Marker,
  Popup,
  Polyline,
  TileLayer,
  useMap,
} from "react-leaflet";

import {
  buscarZonaMapa,
  calcularRutaProbableAtacante,
  obtenerCamarasMapa,
  obtenerZonasMapa,
} from "../services/mapa.service";
import type {
  MapaCamara,
  PuntoMapa,
  RutaEscapeMapa,
  RutaProbableAtacanteFeature,
  ZonaRiesgoMapa,
} from "../types/mapa.types";

type Props = {
  activeSection?: string;
  ultimaDeteccion?: any;
  calcularRutaTrigger?: number;
  onCalculandoRutaChange?: (calculando: boolean) => void;
  busquedaZonaTexto?: string;
  busquedaZonaTrigger?: number;
  onZonaSeleccionadaChange?: (zona: ZonaRiesgoMapa | null) => void;
  onRutasEscapeChange?: (rutas: RutaEscapeMapa[]) => void;
  onMensajeBusquedaChange?: (mensaje: string) => void;
};

const GDL_CENTER: [number, number] = [20.6736, -103.344];

const COLORES_RUTA = ["#ef4444", "#f97316", "#eab308", "#38bdf8"];

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

function normalizarTexto(texto?: string) {
  return (texto || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();
}

function distanciaKm(
  puntoA: { latitud: number; longitud: number },
  puntoB: { latitud: number; longitud: number }
) {
  const radioTierraKm = 6371;

  const lat1 = (puntoA.latitud * Math.PI) / 180;
  const lat2 = (puntoB.latitud * Math.PI) / 180;
  const deltaLat = ((puntoB.latitud - puntoA.latitud) * Math.PI) / 180;
  const deltaLon = ((puntoB.longitud - puntoA.longitud) * Math.PI) / 180;

  const a =
    Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
    Math.cos(lat1) *
      Math.cos(lat2) *
      Math.sin(deltaLon / 2) *
      Math.sin(deltaLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return radioTierraKm * c;
}

function camaraPerteneceAZona(camara: MapaCamara, zona: ZonaRiesgoMapa) {
  const zonaCamara = normalizarTexto(camara.zona);
  const nombreZona = normalizarTexto(zona.nombre);

  const coincidePorNombre =
    zonaCamara.length > 0 &&
    (zonaCamara === nombreZona ||
      zonaCamara.includes(nombreZona) ||
      nombreZona.includes(zonaCamara));

  const distancia = distanciaKm(
    {
      latitud: camara.latitud,
      longitud: camara.longitud,
    },
    {
      latitud: zona.latitud,
      longitud: zona.longitud,
    }
  );

  const radioBusquedaKm = Math.max((zona.radio || 500) / 1000 + 0.5, 1);

  return coincidePorNombre || distancia <= radioBusquedaKm;
}

function obtenerNumero(valor: unknown, fallback = 0) {
  const numero = Number(valor);

  return Number.isFinite(numero) ? numero : fallback;
}

function obtenerPropiedadNumerica(
  ruta: RutaProbableAtacanteFeature,
  propiedad: string,
  fallback = 0
) {
  return obtenerNumero(ruta.properties?.[propiedad], fallback);
}

function obtenerPropiedadTexto(
  ruta: RutaProbableAtacanteFeature,
  propiedad: string,
  fallback = "N/D"
) {
  const valor = ruta.properties?.[propiedad];

  if (typeof valor === "string" && valor.trim().length > 0) {
    return valor;
  }

  return fallback;
}

function convertirRutaAResumen(
  ruta: RutaProbableAtacanteFeature,
  index: number
): RutaEscapeMapa {
  const direccion = obtenerPropiedadTexto(ruta, "direccion", `Ruta ${index + 1}`);
  const probabilidad = obtenerPropiedadNumerica(
    ruta,
    "probabilidad_operativa",
    0
  );
  const riesgo = obtenerPropiedadNumerica(ruta, "riesgo_zonas", 0);
  const distancia = obtenerPropiedadNumerica(ruta, "distancia_m", 0);
  const color = COLORES_RUTA[index % COLORES_RUTA.length];

  return {
    id: index + 1,
    color,
    distancia,
    duracion: 0,
    instrucciones: [
      {
        texto: `Ruta probable hacia ${direccion}.`,
      },
      {
        texto: `Score operativo: ${probabilidad.toFixed(2)}%.`,
      },
      {
        texto: `Riesgo de zonas cercanas: ${riesgo.toFixed(2)}%.`,
      },
      {
        texto: `Distancia estimada: ${Math.round(distancia)} m.`,
      },
    ],
  };
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

function RoutesFitController({
  rutas,
}: {
  rutas: RutaProbableAtacanteFeature[];
}) {
  const map = useMap();

  useEffect(() => {
    const puntos = rutas.flatMap((ruta) =>
      ruta.geometry?.coordinates?.map(([lon, lat]) => [lat, lon] as [number, number]) || []
    );

    if (puntos.length === 0) {
      return;
    }

    map.fitBounds(puntos, {
      padding: [40, 40],
    });
  }, [map, rutas]);

  return null;
}

export function SecurityMap({
  activeSection,
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
  const [rutasAtacante, setRutasAtacante] = useState<
    RutaProbableAtacanteFeature[]
  >([]);

  const mostrarMapaCompleto =
    activeSection === "zonas" ||
    activeSection === "estadisticas" ||
    activeSection === "stats";

  const zonasVisibles = mostrarMapaCompleto
    ? zonas
    : zonaSeleccionada
      ? [zonaSeleccionada]
      : [];

  const camarasVisibles = mostrarMapaCompleto
    ? camaras
    : zonaSeleccionada
      ? camaras.filter((camara) =>
          camaraPerteneceAZona(camara, zonaSeleccionada)
        )
      : [];

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
    if (!ultimaDeteccion) {
      return;
    }

    const puntoDeteccion = obtenerPuntoDesdeDeteccion();

    if (!puntoDeteccion) {
      return;
    }

    setSelectedPoint(puntoDeteccion);
  }, [ultimaDeteccion]);

  useEffect(() => {
    if (calcularRutaTrigger <= 0) {
      return;
    }

    calcularRutasProbablesAtacante();
  }, [calcularRutaTrigger]);

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
    setRutasAtacante([]);

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
        setZonaSeleccionada(null);
        setRutasAtacante([]);
        onZonaSeleccionadaChange?.(null);
        onRutasEscapeChange?.([]);
        onMensajeBusquedaChange?.(`No se encontró una colonia con: ${query}`);
        return;
      }

      seleccionarZona(zona);
    } catch (error) {
      console.error("Error buscando zona:", error);
      onMensajeBusquedaChange?.("Error buscando la colonia.");
    }
  }

  function obtenerPuntoDesdeDeteccion(): PuntoMapa | null {
    if (ultimaDeteccion?.latitud && ultimaDeteccion?.longitud) {
      return {
        lat: Number(ultimaDeteccion.latitud),
        lng: Number(ultimaDeteccion.longitud),
      };
    }

    if (ultimaDeteccion?.lat && ultimaDeteccion?.lon) {
      return {
        lat: Number(ultimaDeteccion.lat),
        lng: Number(ultimaDeteccion.lon),
      };
    }

    if (ultimaDeteccion?.lat && ultimaDeteccion?.lng) {
      return {
        lat: Number(ultimaDeteccion.lat),
        lng: Number(ultimaDeteccion.lng),
      };
    }

    const camaraDetectada = camaras.find(
      (camara) => camara.id === ultimaDeteccion?.camara_id
    );

    if (camaraDetectada) {
      return {
        lat: camaraDetectada.latitud,
        lng: camaraDetectada.longitud,
      };
    }

    return null;
  }

  function obtenerOrigenParaRutasAtacante() {
    if (selectedPoint) {
      return {
        lat: selectedPoint.lat,
        lon: selectedPoint.lng,
      };
    }

    const puntoDeteccion = obtenerPuntoDesdeDeteccion();

    if (puntoDeteccion) {
      return {
        lat: puntoDeteccion.lat,
        lon: puntoDeteccion.lng,
      };
    }

    if (zonaSeleccionada) {
      return {
        lat: zonaSeleccionada.latitud,
        lon: zonaSeleccionada.longitud,
      };
    }

    return null;
  }

  async function calcularRutasProbablesAtacante() {
    const origen = obtenerOrigenParaRutasAtacante();

    if (!origen) {
      onMensajeBusquedaChange?.(
        "Selecciona una zona, cámara o detección para calcular rutas probables del atacante."
      );
      return;
    }

    try {
      onCalculandoRutaChange?.(true);
      onRutasEscapeChange?.([]);
      setRutasAtacante([]);

      const respuesta = await calcularRutaProbableAtacante(origen);
      const rutas = (respuesta.geojson?.features || []).filter(
        (feature) =>
          feature.geometry?.type === "LineString" &&
          Array.isArray(feature.geometry.coordinates) &&
          feature.geometry.coordinates.length >= 2
      );
      const primerasCuatroRutas = rutas.slice(0, 4);

      setRutasAtacante(primerasCuatroRutas);
      onRutasEscapeChange?.(
        primerasCuatroRutas.map((ruta, index) =>
          convertirRutaAResumen(ruta, index)
        )
      );

      if (primerasCuatroRutas.length === 0) {
        onMensajeBusquedaChange?.(
          "La IA respondió, pero no regresó rutas trazables para el mapa."
        );
        return;
      }

      onMensajeBusquedaChange?.(
        `Ruta probable: ${respuesta.direccion_probable}. Score operativo: ${Number(
          respuesta.probabilidad_operativa || 0
        ).toFixed(2)}%.`
      );
    } catch (error) {
      console.error("Error calculando rutas probables del atacante:", error);
      onMensajeBusquedaChange?.(
        "No se pudieron calcular las rutas probables del atacante."
      );
    } finally {
      onCalculandoRutaChange?.(false);
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

        {zonasVisibles.map((zona, index) => {
          const selected = zonaSeleccionada?.id === zona.id;
          const color = colorPorRiesgoValor(zona.riesgo);
          const radio = zona.radio || radioPorRiesgo(zona.riesgo);

          return (
            <Fragment key={`${zona.id}-${index}`}>
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

        {camarasVisibles.map((camara) => {
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
                  setRutasAtacante([]);
                  onRutasEscapeChange?.([]);
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

        {selectedPoint && rutasAtacante.length > 0 && (
          <CircleMarker
            center={[selectedPoint.lat, selectedPoint.lng]}
            radius={9}
            pathOptions={{
              color: "#ffffff",
              weight: 2,
              fillColor: "#dc2626",
              fillOpacity: 1,
            }}
          >
            <Popup>
              <strong>Punto de detección</strong>
              <br />
              Origen usado para calcular rutas probables del atacante.
            </Popup>
          </CircleMarker>
        )}

        {rutasAtacante.map((ruta, index) => {
          const puntos = ruta.geometry.coordinates.map(([lon, lat]) => [
            lat,
            lon,
          ]) as [number, number][];
          const color = COLORES_RUTA[index % COLORES_RUTA.length];
          const direccion = obtenerPropiedadTexto(
            ruta,
            "direccion",
            `Ruta ${index + 1}`
          );
          const probabilidad = obtenerPropiedadNumerica(
            ruta,
            "probabilidad_operativa",
            0
          );
          const riesgo = obtenerPropiedadNumerica(ruta, "riesgo_zonas", 0);
          const distancia = obtenerPropiedadNumerica(ruta, "distancia_m", 0);

          return (
            <Polyline
              key={`ruta-atacante-${index}`}
              positions={puntos}
              pathOptions={{
                color,
                weight: index === 0 ? 6 : 4,
                opacity: index === 0 ? 0.95 : 0.7,
                dashArray: index === 0 ? undefined : "8 8",
              }}
            >
              <Popup>
                <div style={{ minWidth: 210 }}>
                  <strong>Ruta probable del atacante #{index + 1}</strong>
                  <br />
                  Dirección: <strong>{direccion}</strong>
                  <br />
                  Score operativo: <strong>{probabilidad.toFixed(2)}%</strong>
                  <br />
                  Riesgo de zonas: <strong>{riesgo.toFixed(2)}%</strong>
                  <br />
                  Distancia: <strong>{Math.round(distancia)} m</strong>
                </div>
              </Popup>
            </Polyline>
          );
        })}

        <MapController selectedPoint={selectedPoint} />
        <RoutesFitController rutas={rutasAtacante} />
      </MapContainer>
    </div>
  );
}
