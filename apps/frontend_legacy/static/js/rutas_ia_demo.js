let rutaProbableRoutingControl = null;
let rutaProbableFallbackLayer = null;

let rutaSeguraRoutingControl = null;
let rutaSeguraFallbackLayer = null;

let ultimaRutaProbablePintadaId = null;
let pollingRutaProbableId = null;

let cacheColonias = [];
let cachePuntosTuristicos = [];

const RUTAS_API_BASE = "/api/ia-rutas";

function getMapa() {
  return window.map;
}

function normalizarTexto(texto) {
  return String(texto || "")
    .trim()
    .toUpperCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function aplicarAliasTuristico(texto) {
  const normalizado = normalizarTexto(texto);

  const aliases = {
    "ESTADIO AKCRON": "ESTADIO AKRON",
    "AKCRON": "AKRON",
    "PLAZA ANDARES": "ANDARES",
    "ANDARES": "ANDARES",
    "CATEDRAL": "CATEDRAL",
    "CATEDRAL DE GUADALAJARA": "CATEDRAL",
    "MERCADO LIBERTAD": "MERCADO LIBERTAD",
    "SAN JUAN DE DIOS": "MERCADO LIBERTAD",
    "MUSEO CABANAS": "MUSEO CABANAS",
    "INSTITUTO CULTURAL CABANAS": "MUSEO CABANAS"
  };

  return aliases[normalizado] || normalizado;
}

function obtenerColorPorRiesgo(riesgo) {
  if (riesgo >= 70) return "#dc2626";
  if (riesgo >= 45) return "#f97316";
  return "#16a34a";
}

function extraerArrayRespuesta(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data.items)) return data.items;
  if (Array.isArray(data.data)) return data.data;
  if (Array.isArray(data.resultado)) return data.resultado;
  if (Array.isArray(data.colonias)) return data.colonias;
  if (Array.isArray(data.puntos)) return data.puntos;
  return [];
}

async function cargarJsonSeguro(url) {
  try {
    const response = await fetch(url);

    if (!response.ok) {
      console.warn(`No se pudo cargar ${url}. HTTP ${response.status}`);
      return [];
    }

    const data = await response.json();
    return extraerArrayRespuesta(data);
  } catch (error) {
    console.warn(`Error cargando ${url}:`, error);
    return [];
  }
}

async function cargarCatalogosRutasIA() {
  try {
    if (window.GDL_CONFIG?.apiColonias) {
      const responseColonias = await fetch(window.GDL_CONFIG.apiColonias);
      const dataColonias = await responseColonias.json();
      cacheColonias = extraerArrayRespuesta(dataColonias);
      console.log("Colonias cargadas para rutas IA:", cacheColonias.length);
    }

    if (window.GDL_CONFIG?.apiPuntosTuristicos) {
      const responsePuntos = await fetch(window.GDL_CONFIG.apiPuntosTuristicos);
      const dataPuntos = await responsePuntos.json();
      cachePuntosTuristicos = extraerArrayRespuesta(dataPuntos);
      console.log("Puntos turísticos cargados desde API:", cachePuntosTuristicos.length);
    }

    if (!cachePuntosTuristicos || cachePuntosTuristicos.length === 0) {
      console.warn("API de puntos turísticos regresó 0. Cargando JSON local...");

      const puntosJson = await cargarJsonSeguro(
        "/static/modules/gdl_turismo/data/gdl_puntos_turisticos_ruta.json"
      );

      const zonasJson = await cargarJsonSeguro(
        "/static/modules/gdl_turismo/data/gdl_zonas_turisticas_normalizadas.json"
      );

      cachePuntosTuristicos = [
        ...puntosJson,
        ...zonasJson
      ];

      console.log("Puntos turísticos cargados desde JSON local:", cachePuntosTuristicos.length);
    }

  } catch (error) {
    console.error("Error cargando catálogos para rutas IA:", error);
  }
}

function obtenerNombreItem(item) {
  return (
    item.nombre_colonia ||
    item.nombre ||
    item.nombre_zona ||
    item.name ||
    item.label ||
    ""
  );
}

function obtenerLatLonItem(item) {
  const lat = Number(item.lat ?? item.latitude ?? item.centro?.lat);
  const lon = Number(item.lon ?? item.lng ?? item.longitud ?? item.longitude ?? item.centro?.lon);

  if (Number.isFinite(lat) && Number.isFinite(lon)) {
    return { lat, lon };
  }

  return null;
}

function buscarEnCatalogoPorTexto(catalogo, texto) {
  const objetivo = aplicarAliasTuristico(texto);

  if (!objetivo) return null;

  return catalogo.find((item) => {
    const nombre = aplicarAliasTuristico(obtenerNombreItem(item));

    return (
      nombre === objetivo ||
      nombre.includes(objetivo) ||
      objetivo.includes(nombre)
    );
  });
}

function obtenerTextoDeSelect(selectId) {
  const select = document.getElementById(selectId);

  if (!select) return "";

  const selectedOption = select.options[select.selectedIndex];

  return selectedOption?.textContent || select.value || "";
}

function obtenerPuntoFormulario(prefix) {
  const tipo = document.getElementById(`${prefix}Tipo`)?.value || "colonia";

  if (tipo === "turistico") {
    const selectId = `${prefix}Turistico`;
    const selectValue = document.getElementById(selectId)?.value || "";
    const selectText = obtenerTextoDeSelect(selectId);

    const punto =
      buscarEnCatalogoPorTexto(cachePuntosTuristicos, selectValue) ||
      buscarEnCatalogoPorTexto(cachePuntosTuristicos, selectText);

    if (!punto) {
      throw new Error(`No encontré coordenadas para el ${prefix} turístico: ${selectText || selectValue}`);
    }

    const coords = obtenerLatLonItem(punto);

    if (!coords) {
      throw new Error(`El ${prefix} turístico no tiene lat/lon válido.`);
    }

    return coords;
  }

  const inputValue = document.getElementById(prefix)?.value || "";

  const colonia = buscarEnCatalogoPorTexto(cacheColonias, inputValue);

  if (!colonia) {
    throw new Error(`No encontré coordenadas para la colonia de ${prefix}: ${inputValue}`);
  }

  const coords = obtenerLatLonItem(colonia);

  if (!coords) {
    throw new Error(`La colonia de ${prefix} no tiene lat/lon válido.`);
  }

  return coords;
}

function obtenerLineStringFeature(geojson) {
  if (!geojson) return null;

  if (geojson.type === "Feature" && geojson.geometry?.type === "LineString") {
    return geojson;
  }

  if (geojson.type === "FeatureCollection") {
    return geojson.features.find(
      (feature) => feature.geometry?.type === "LineString"
    );
  }

  return null;
}

function obtenerPointFeatures(geojson) {
  if (!geojson) return [];

  if (geojson.type === "Feature" && geojson.geometry?.type === "Point") {
    return [geojson];
  }

  if (geojson.type === "FeatureCollection") {
    return geojson.features.filter(
      (feature) => feature.geometry?.type === "Point"
    );
  }

  return [];
}

function limpiarRutaProbable() {
  const mapa = getMapa();
  if (!mapa) return;

  if (rutaProbableRoutingControl) {
    mapa.removeControl(rutaProbableRoutingControl);
    rutaProbableRoutingControl = null;
  }

  if (rutaProbableFallbackLayer) {
    mapa.removeLayer(rutaProbableFallbackLayer);
    rutaProbableFallbackLayer = null;
  }
}

function limpiarRutaSegura() {
  const mapa = getMapa();
  if (!mapa) return;

  if (rutaSeguraRoutingControl) {
    mapa.removeControl(rutaSeguraRoutingControl);
    rutaSeguraRoutingControl = null;
  }

  if (rutaSeguraFallbackLayer) {
    mapa.removeLayer(rutaSeguraFallbackLayer);
    rutaSeguraFallbackLayer = null;
  }
}

function crearMarcadoresPuntos(pointFeatures, colorHex) {
  const markers = [];

  pointFeatures.forEach((feature) => {
    const coords = feature.geometry.coordinates;
    const lon = coords[0];
    const lat = coords[1];

    const marker = L.circleMarker([lat, lon], {
      radius: 9,
      color: "#111827",
      weight: 2,
      fillColor: colorHex,
      fillOpacity: 1
    });

    const tipo = feature.properties?.tipo || "punto";

    marker.bindPopup(`
      <strong>Punto de ruta</strong><br/>
      Tipo: ${tipo}<br/>
      Lat: ${lat}<br/>
      Lon: ${lon}
    `);

    markers.push(marker);
  });

  return markers;
}

function pintarFallbackGeoJSON({
  geojson,
  color,
  dashArray,
  popupTitle,
  propiedades,
  target
}) {
  const mapa = getMapa();

  const layer = L.geoJSON(geojson, {
    style: function () {
      return {
        color,
        weight: 6,
        opacity: 0.95,
        dashArray
      };
    },
    pointToLayer: function (feature, latlng) {
      return L.circleMarker(latlng, {
        radius: 9,
        color: "#111827",
        weight: 2,
        fillColor: target === "segura" ? "#22c55e" : "#facc15",
        fillOpacity: 1
      });
    },
    onEachFeature: function (feature, layer) {
      const props = feature.properties || {};

      layer.bindPopup(`
        <strong>${popupTitle}</strong><br/>
        Tipo: ${props.tipo_ruta || propiedades.tipo_ruta || "N/D"}<br/>
        Riesgo: ${props.riesgo_zonas || props.score_riesgo || propiedades.score_riesgo || "N/D"}<br/>
        Dirección: ${props.direccion || propiedades.direccion_probable || "N/D"}
      `);
    }
  }).addTo(mapa);

  if (target === "segura") {
    rutaSeguraFallbackLayer = layer;
  } else {
    rutaProbableFallbackLayer = layer;
  }
}

function pintarRutaPorCalles({
  geojson,
  propiedades = {},
  target,
  color,
  popupTitle,
  dashArray
}) {
  const mapa = getMapa();

  if (!mapa) {
    console.error("No existe window.map.");
    return;
  }

  if (!geojson) {
    console.warn("No hay GeoJSON para pintar.");
    return;
  }

  if (target === "segura") {
    limpiarRutaSegura();
  } else {
    limpiarRutaProbable();
  }

  const lineFeature = obtenerLineStringFeature(geojson);
  const pointFeatures = obtenerPointFeatures(geojson);

  if (!lineFeature) {
    console.warn("No encontré LineString en el GeoJSON. Pintando fallback.");
    pintarFallbackGeoJSON({ geojson, color, dashArray, popupTitle, propiedades, target });
    return;
  }

  const coords = lineFeature.geometry.coordinates;

  if (!coords || coords.length < 2) {
    console.warn("La ruta no tiene suficientes coordenadas.");
    return;
  }

  const waypoints = coords.map(([lon, lat]) => L.latLng(lat, lon));

  if (!L.Routing) {
    console.warn("Leaflet Routing Machine no está cargado. Pintando línea simple.");
    pintarFallbackGeoJSON({ geojson, color, dashArray, popupTitle, propiedades, target });
    return;
  }

  const routingControl = L.Routing.control({
    waypoints,
    addWaypoints: false,
    routeWhileDragging: false,
    draggableWaypoints: false,
    fitSelectedRoutes: target === "segura",
    show: false,
    createMarker: function () {
      return null;
    },
    lineOptions: {
      styles: [
        {
          color,
          weight: target === "segura" ? 8 : 7,
          opacity: 0.95,
          dashArray
        }
      ]
    },
    router: L.Routing.osrmv1({
      serviceUrl: "https://router.project-osrm.org/route/v1"
    })
  }).addTo(mapa);

  routingControl.on("routesfound", function (event) {
    const route = event.routes[0];

    if (!route) return;

    const summary = route.summary;

    console.log(`${popupTitle} por calles calculada:`, {
      distancia_m: summary.totalDistance,
      tiempo_s: summary.totalTime
    });
  });

  routingControl.on("routingerror", function (error) {
    console.warn(`No se pudo calcular ${popupTitle} por calles. Pintando fallback.`, error);

    if (target === "segura" && rutaSeguraRoutingControl) {
      mapa.removeControl(rutaSeguraRoutingControl);
      rutaSeguraRoutingControl = null;
    }

    if (target === "probable" && rutaProbableRoutingControl) {
      mapa.removeControl(rutaProbableRoutingControl);
      rutaProbableRoutingControl = null;
    }

    pintarFallbackGeoJSON({ geojson, color, dashArray, popupTitle, propiedades, target });
  });

  const markers = crearMarcadoresPuntos(
    pointFeatures,
    target === "segura" ? "#22c55e" : "#facc15"
  );

  markers.forEach((marker) => marker.addTo(mapa));

  if (target === "segura") {
    rutaSeguraRoutingControl = routingControl;
    rutaSeguraFallbackLayer = L.layerGroup(markers).addTo(mapa);
  } else {
    rutaProbableRoutingControl = routingControl;
    rutaProbableFallbackLayer = L.layerGroup(markers).addTo(mapa);
  }
}

async function cargarUltimaRutaProbable() {
  try {
    const response = await fetch(
      `${RUTAS_API_BASE}/rutas-recientes?tipo_ruta=ruta_probable_desplazamiento&limit=1`
    );

    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status}`);
    }

    const data = await response.json();

    if (!data.items || data.items.length === 0) {
      return;
    }

    const ruta = data.items[0];

    if (ruta.id_ruta === ultimaRutaProbablePintadaId) {
      return;
    }

    ultimaRutaProbablePintadaId = ruta.id_ruta;

    console.log("Pintando nueva ruta probable:", ruta);

    pintarRutaPorCalles({
      geojson: ruta.geojson,
      propiedades: {
        tipo_ruta: ruta.tipo_ruta,
        score_riesgo: ruta.score_riesgo,
        distancia_m: ruta.distancia_m,
        algoritmo: ruta.algoritmo,
        direccion_probable: ruta.parametros?.direccion_probable,
        probabilidad_operativa: ruta.parametros?.probabilidad_operativa
      },
      target: "probable",
      color: "#f97316",
      popupTitle: "Ruta probable de desplazamiento",
      dashArray: "10, 8"
    });

  } catch (error) {
    console.error("Error cargando última ruta probable:", error);
  }
}

async function calcularRutaSeguraDesdeFormulario() {
  try {
    const origen = obtenerPuntoFormulario("origen");
    const destino = obtenerPuntoFormulario("destino");

    console.log("Calculando ruta segura:", { origen, destino });

    const response = await fetch(`${RUTAS_API_BASE}/ruta-segura`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        origen,
        destino,
        guardar: true
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || data.detalle || `Error HTTP ${response.status}`);
    }

    console.log("Ruta segura calculada:", data);

    pintarRutaPorCalles({
      geojson: data.geojson,
      propiedades: {
        tipo_ruta: data.tipo_ruta,
        score_riesgo: data.riesgo_ajustado,
        distancia_m: data.distancia_m,
        algoritmo: data.algoritmo
      },
      target: "segura",
      color: "#16a34a",
      popupTitle: "Ruta segura recomendada",
      dashArray: null
    });

    actualizarResumenRutaSegura(data);

  } catch (error) {
    console.error("Error calculando ruta segura:", error);
    alert(error.message || "No se pudo calcular la ruta segura.");
  }
}

function actualizarResumenRutaSegura(data) {
  const riesgoRuta = document.getElementById("riesgoRuta");
  const distanciaRuta = document.getElementById("distanciaRuta");
  const tiempoRuta = document.getElementById("tiempoRuta");
  const coloniasCriticas = document.getElementById("coloniasCriticas");

  if (riesgoRuta) {
    riesgoRuta.textContent = `${data.riesgo_ajustado ?? "--"}/100`;
  }

  if (distanciaRuta) {
    distanciaRuta.textContent = data.distancia_m
      ? `${(data.distancia_m / 1000).toFixed(2)} km`
      : "--";
  }

  if (tiempoRuta) {
    tiempoRuta.textContent = data.duracion_estimada_min
      ? `${data.duracion_estimada_min} min`
      : "--";
  }

  if (coloniasCriticas) {
    const zonas = data.zonas_influyentes || [];
    const nombres = zonas
      .filter((zona) => Number(zona.riesgo) >= 50)
      .slice(0, 3)
      .map((zona) => zona.nombre);

    coloniasCriticas.textContent = nombres.length ? nombres.join(", ") : "Sin críticas";
  }
}

function conectarBotonRutaSegura() {
  const btnCalcular = document.getElementById("btnCalcular");

  if (!btnCalcular) {
    console.warn("No existe btnCalcular.");
    return;
  }

  btnCalcular.addEventListener("click", function (event) {
    event.preventDefault();
    event.stopPropagation();
    event.stopImmediatePropagation();

    calcularRutaSeguraDesdeFormulario();
  }, true);
}

function iniciarPollingRutaProbable() {
  if (pollingRutaProbableId) {
    clearInterval(pollingRutaProbableId);
  }

  cargarUltimaRutaProbable();

  pollingRutaProbableId = setInterval(() => {
    cargarUltimaRutaProbable();
  }, 3000);
}

async function inicializarRutasIADemo() {
  await cargarCatalogosRutasIA();

  conectarBotonRutaSegura();
  iniciarPollingRutaProbable();

  console.log("Rutas IA demo inicializado.");
}

function esperarMapaEIniciar(intentos = 0) {
  const mapa = getMapa();

  if (mapa) {
    console.log("Mapa detectado. Inicializando rutas IA.");
    inicializarRutasIADemo();
    return;
  }

  if (intentos >= 20) {
    console.error("No se encontró window.map después de esperar.");
    return;
  }

  setTimeout(() => {
    esperarMapaEIniciar(intentos + 1);
  }, 300);
}

document.addEventListener("DOMContentLoaded", () => {
  esperarMapaEIniciar();
});