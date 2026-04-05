document.addEventListener("DOMContentLoaded", async function () {
  const map = L.map("map").setView([20.6736, -103.3440], 11);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  const POLIGONO_GDL_COORDS = [
    [-103.7677643620951, 20.66055488916858],
    [-103.6263847360454, 20.49401408206751],
    [-103.5904436084843, 20.47304947023955],
    [-103.5430248547833, 20.4338907612765], 
    [-103.5033193223697, 20.42213949556241],
    [-103.4675877369297, 20.41871066543661],
    [-103.4164014028743, 20.42022940065636],
    [-103.3579019626379, 20.38694182019344],
    [-103.2556014310676, 20.39154427131703],
    [-103.1407287226269, 20.51886238471157],
    [-103.1782325674768, 20.66570583846619],
    [-103.2744872156881, 20.76312036082007],
    [-103.4001400471787, 20.80302589777127],
    [-103.5876813605534, 20.81252779083983],
    [-103.7209582819949, 20.89684476618087],
    [-103.8692780195956, 20.93842984561356],
    [-103.7677643620951, 20.66055488916858]
  ];

  const POLIGONO_GDL = turf.polygon([POLIGONO_GDL_COORDS]);

  L.geoJSON(POLIGONO_GDL, {
    style: {
      color: "#334155",
      weight: 2,
      fillOpacity: 0
    }
  }).addTo(map);

  const municipioSelect = document.getElementById("municipio");
  const btnCalcular = document.getElementById("btnCalcular");
  const btnReiniciar = document.getElementById("btnReiniciar");

  const origenTipo = document.getElementById("origenTipo");
  const destinoTipo = document.getElementById("destinoTipo");

  const origenInput = document.getElementById("origen");
  const destinoInput = document.getElementById("destino");

  const origenTuristico = document.getElementById("origenTuristico");
  const destinoTuristico = document.getElementById("destinoTuristico");

  const riesgoRuta = document.getElementById("riesgoRuta");
  const distanciaRuta = document.getElementById("distanciaRuta");
  const tiempoRuta = document.getElementById("tiempoRuta");
  const camarasRuta = document.getElementById("camarasRuta");
  const coloniasCriticas = document.getElementById("coloniasCriticas");

  const toggleHex = document.getElementById("toggleHex");
  const togglePuntos = document.getElementById("togglePuntos");
  const toggleCamaras = document.getElementById("toggleCamaras");
  const toggleTurismo = document.getElementById("toggleTurismo");

  const hexLayer = L.geoJSON(null).addTo(map);
  const puntosLayer = L.featureGroup().addTo(map);
  const rutaLayer = L.featureGroup().addTo(map);
  const camarasLayer = L.featureGroup().addTo(map);
  const turismoHexLayer = L.featureGroup().addTo(map);

  let coloniasActuales = [];
  let puntosTuristicos = [];
  let zonasTuristicas = [];

  function getColorByRisk(riesgo) {
    if (riesgo === null || riesgo === undefined) return "#9ca3af";
    if (riesgo <= 25) return "#22c55e";
    if (riesgo <= 50) return "#eab308";
    if (riesgo <= 75) return "#f97316";
    return "#ef4444";
  }

  function limpiarResumen() {
    riesgoRuta.textContent = "--";
    distanciaRuta.textContent = "--";
    tiempoRuta.textContent = "--";
    camarasRuta.textContent = "--";
    coloniasCriticas.textContent = "--";
  }

  function limpiarCapasRuta() {
    rutaLayer.clearLayers();
    camarasLayer.clearLayers();
  }

  function limpiarCapasDatos() {
    hexLayer.clearLayers();
    puntosLayer.clearLayers();
    turismoHexLayer.clearLayers();
  }

  function distanciaEnKm(lat1, lon1, lat2, lon2) {
    const from = turf.point([lon1, lat1]);
    const to = turf.point([lon2, lat2]);
    return turf.distance(from, to, { units: "kilometers" });
  }

  function generarHexGrid(colonias) {
    const bbox = turf.bbox(POLIGONO_GDL);
    const cellSide = 0.45;

    const gridCompleto = turf.hexGrid(bbox, cellSide, { units: "kilometers" });

    const featuresDentro = gridCompleto.features.filter((feature) => {
      const centro = turf.centroid(feature);
      return turf.booleanPointInPolygon(centro, POLIGONO_GDL);
    });

    const grid = turf.featureCollection(featuresDentro);

    grid.features.forEach((feature, index) => {
      feature.properties = {
        id: index + 1,
        riesgo: null,
        colonia_ref: "Sin dato",
        municipio: "Guadalajara",
        distancia_ref_km: Infinity
      };
    });

    colonias.forEach((colonia) => {
      const hexOrdenados = grid.features
        .map((feature) => {
          const centro = turf.centroid(feature);
          const [lon, lat] = centro.geometry.coordinates;

          return {
            feature,
            distancia: distanciaEnKm(lat, lon, colonia.lat, colonia.lon)
          };
        })
        .sort((a, b) => a.distancia - b.distancia);

      const hexCercanos = hexOrdenados.slice(0, 7);

      hexCercanos.forEach((item) => {
        const actual = item.feature.properties.distancia_ref_km ?? Infinity;

        if (item.distancia < actual) {
          item.feature.properties.riesgo = colonia.riesgo;
          item.feature.properties.colonia_ref = colonia.nombre_colonia;
          item.feature.properties.municipio = colonia.municipio;
          item.feature.properties.distancia_ref_km = item.distancia;
        }
      });
    });

    return grid;
  }

  function renderHexGrid(colonias) {
    hexLayer.clearLayers();

    if (!toggleHex.checked) return;

    const grid = generarHexGrid(colonias || []);
    hexLayer.addData(grid);

    hexLayer.eachLayer((layer) => {
      const riesgo = layer.feature.properties.riesgo;
      const coloniaRef = layer.feature.properties.colonia_ref;
      const distanciaRef = layer.feature.properties.distancia_ref_km;
      const textoRiesgo = riesgo === null ? "Sin dato" : riesgo;

      layer.setStyle({
        color: getColorByRisk(riesgo),
        weight: 1,
        fillColor: getColorByRisk(riesgo),
        fillOpacity: riesgo === null ? 0.18 : 0.35
      });

      layer.bindPopup(`
        <strong>Zona de riesgo</strong><br>
        Riesgo: ${textoRiesgo}<br>
        Colonia de referencia: ${coloniaRef}<br>
        Distancia al dato: ${Number.isFinite(distanciaRef) ? distanciaRef.toFixed(2) + " km" : "--"}
      `);
    });
  }

  function renderPuntos(colonias) {
    puntosLayer.clearLayers();

    if (!togglePuntos.checked) return;

    colonias.forEach((colonia) => {
      L.circleMarker([colonia.lat, colonia.lon], {
        radius: 4,
        color: "#111827",
        fillColor: getColorByRisk(colonia.riesgo),
        fillOpacity: 0.9,
        weight: 1
      })
        .bindPopup(`
          <strong>${colonia.nombre_colonia}</strong><br>
          Municipio: ${colonia.municipio}<br>
          Riesgo: ${colonia.riesgo}
        `)
        .addTo(puntosLayer);
    });
  }

  function convertirPoligonoALonLat(poligonoLatLon) {
    return poligonoLatLon.map(([lat, lon]) => [lon, lat]);
  }

  function generarHexagonosDentroDePoligono(poligonoLatLon, cellSide = 0.02) {
    const coordsLonLat = convertirPoligonoALonLat(poligonoLatLon);
    const turfPolygon = turf.polygon([coordsLonLat]);
    const bbox = turf.bbox(turfPolygon);

    const grid = turf.hexGrid(bbox, cellSide, { units: "kilometers" });

    const hexDentro = grid.features.filter((feature) => {
      const centro = turf.centroid(feature);
      return turf.booleanPointInPolygon(centro, turfPolygon);
    });

    return turf.featureCollection(hexDentro);
  }

  async function cargarZonasTuristicas() {
    turismoHexLayer.clearLayers();

    if (!toggleTurismo.checked) return;

    try {
      const response = await fetch("/static/data/zonas_turisticas_normalizadas.json");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      zonasTuristicas = await response.json();
    } catch (error) {
      console.warn("No se pudieron cargar zonas_turisticas_normalizadas.json", error);
      zonasTuristicas = [];
      return;
    }

    zonasTuristicas.forEach((zona) => {
      if (zona.poligono && zona.poligono.length >= 3) {
        const gridTurismo = generarHexagonosDentroDePoligono(zona.poligono, 0.02);

        const capaHex = L.geoJSON(gridTurismo, {
          style: {
            color: "#7c3aed",
            weight: 1,
            fillColor: "#a78bfa",
            fillOpacity: 0.22
          }
        }).addTo(turismoHexLayer);

        capaHex.eachLayer((layer) => {
          layer.bindPopup(`
            <strong>${zona.nombre_zona}</strong><br>
            Municipio: ${zona.municipio}<br>
            Riesgo: ${zona.riesgo}
          `);
        });
      } else if (zona.centro) {
        L.circleMarker([zona.centro.lat, zona.centro.lon], {
          radius: 6,
          color: "#2563eb",
          fillColor: "#60a5fa",
          fillOpacity: 0.9
        })
          .bindPopup(`
            <strong>${zona.nombre_zona}</strong><br>
            Municipio: ${zona.municipio}<br>
            Riesgo: ${zona.riesgo}
          `)
          .addTo(turismoHexLayer);
      }
    });
  }

  async function cargarPuntosTuristicos() {
    origenTuristico.innerHTML = '<option value="">Selecciona un punto</option>';
    destinoTuristico.innerHTML = '<option value="">Selecciona un punto</option>';

    try {
      const response = await fetch("/static/data/puntos_turisticos_ruta.json");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      puntosTuristicos = await response.json();
    } catch (error) {
      console.warn("No se pudieron cargar puntos_turisticos_ruta.json", error);
      puntosTuristicos = [];
      return;
    }

    puntosTuristicos.forEach((punto, index) => {
      const option1 = document.createElement("option");
      option1.value = index;
      option1.textContent = punto.nombre;
      origenTuristico.appendChild(option1);

      const option2 = document.createElement("option");
      option2.value = index;
      option2.textContent = punto.nombre;
      destinoTuristico.appendChild(option2);
    });
  }

  function llenarListaColonias(colonias) {
    const datalist = document.getElementById("coloniasList");
    if (!datalist) return;

    datalist.innerHTML = "";

    colonias.forEach((colonia) => {
      const option = document.createElement("option");
      option.value = colonia.nombre_colonia;
      datalist.appendChild(option);
    });
  }

  async function cargarColonias() {
    const municipio = municipioSelect.value;

    try {
      const response = await fetch(`/api/colonias?municipio=${encodeURIComponent(municipio)}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      coloniasActuales = await response.json();
    } catch (error) {
      console.warn("No se pudieron cargar colonias", error);
      coloniasActuales = [];
    }

    llenarListaColonias(coloniasActuales);
    renderHexGrid(coloniasActuales);
    renderPuntos(coloniasActuales);
    await cargarZonasTuristicas();

    if (hexLayer.getBounds().isValid()) {
      map.fitBounds(hexLayer.getBounds(), { padding: [20, 20] });
    }
  }

  function zoomAPunto(lat, lon, nombre = "Punto seleccionado") {
    rutaLayer.clearLayers();

    map.flyTo([lat, lon], 16, { duration: 1.2 });

    L.circleMarker([lat, lon], {
      radius: 8,
      color: "#0f172a",
      fillColor: "#38bdf8",
      fillOpacity: 0.95,
      weight: 2
    })
      .bindPopup(nombre)
      .addTo(rutaLayer)
      .openPopup();
  }

  function buscarColoniaPorNombre(nombre) {
    const texto = nombre.trim().toLowerCase();
    return coloniasActuales.find((c) =>
      c.nombre_colonia.toLowerCase() === texto ||
      c.nombre_colonia.toLowerCase().includes(texto)
    );
  }

  function obtenerPuntoDesdeUI(tipoSelect, textoInput, turisticoSelect) {
    if (tipoSelect.value === "turistico") {
      const idx = turisticoSelect.value;
      if (idx === "") return null;
      return puntosTuristicos[Number(idx)] ?? null;
    }

    const colonia = buscarColoniaPorNombre(textoInput.value);
    if (!colonia) return null;

    return {
      nombre: colonia.nombre_colonia,
      lat: colonia.lat,
      lon: colonia.lon,
      riesgo: colonia.riesgo
    };
  }

  function generarCamarasDemoCercaRuta(origen, destino) {
    camarasLayer.clearLayers();

    if (!toggleCamaras.checked) return 0;

    const camaras = [
      { id: "CAM-001", lat: origen.lat + 0.01, lon: origen.lon + 0.01 },
      { id: "CAM-002", lat: (origen.lat + destino.lat) / 2, lon: (origen.lon + destino.lon) / 2 },
      { id: "CAM-003", lat: destino.lat - 0.01, lon: destino.lon - 0.01 }
    ];

    camaras.forEach((cam) => {
      L.marker([cam.lat, cam.lon])
        .bindPopup(`Cámara ${cam.id}`)
        .addTo(camarasLayer);
    });

    return camaras.length;
  }

  function construirRutaDemo(origen, destino, tipoRuta) {
    const midLat = (origen.lat + destino.lat) / 2;
    const midLon = (origen.lon + destino.lon) / 2;
    const offset = tipoRuta === "segura" ? 0.015 : -0.008;

    return [
      [origen.lat, origen.lon],
      [midLat + offset, midLon - offset],
      [destino.lat, destino.lon]
    ];
  }

  function calcularResumenRuta(origen, destino) {
    const distancia = distanciaEnKm(origen.lat, origen.lon, destino.lat, destino.lon);
    return {
      distanciaKm: distancia,
      tiempoMin: Math.max(5, Math.round(distancia * 3.5))
    };
  }

  function actualizarCamposSegunTipo() {
    const origenEsTuristico = origenTipo.value === "turistico";
    const destinoEsTuristico = destinoTipo.value === "turistico";

    origenInput.disabled = origenEsTuristico;
    origenTuristico.disabled = !origenEsTuristico;

    destinoInput.disabled = destinoEsTuristico;
    destinoTuristico.disabled = !destinoEsTuristico;
  }

  function manejarCambioColonia(input, prefijo) {
    const colonia = buscarColoniaPorNombre(input.value);
    if (!colonia) return;
    zoomAPunto(colonia.lat, colonia.lon, `${prefijo}: ${colonia.nombre_colonia}`);
  }

  btnCalcular.addEventListener("click", function () {
    const tipoRuta = document.querySelector('input[name="tipoRuta"]:checked')?.value || "segura";

    const origen = obtenerPuntoDesdeUI(origenTipo, origenInput, origenTuristico);
    const destino = obtenerPuntoDesdeUI(destinoTipo, destinoInput, destinoTuristico);

    if (!origen || !destino) {
      alert("Selecciona un origen y un destino válidos.");
      return;
    }

    limpiarCapasRuta();

    const ruta = construirRutaDemo(origen, destino, tipoRuta);
    const resumen = calcularResumenRuta(origen, destino);
    const totalCamaras = generarCamarasDemoCercaRuta(origen, destino);

    const colorRuta = tipoRuta === "segura" ? "#2563eb" : "#7c3aed";

    const polyline = L.polyline(ruta, {
      color: colorRuta,
      weight: 5
    }).addTo(rutaLayer);

    L.marker([origen.lat, origen.lon])
      .bindPopup(`Origen: ${origen.nombre}`)
      .addTo(rutaLayer);

    L.marker([destino.lat, destino.lon])
      .bindPopup(`Destino: ${destino.nombre}`)
      .addTo(rutaLayer);

    riesgoRuta.textContent = tipoRuta === "segura" ? "Medio-Bajo" : "Medio";
    distanciaRuta.textContent = `${resumen.distanciaKm.toFixed(2)} km`;
    tiempoRuta.textContent = `${resumen.tiempoMin} min`;
    camarasRuta.textContent = totalCamaras;
    coloniasCriticas.textContent = "Demo";

    map.fitBounds(polyline.getBounds(), { padding: [30, 30] });
  });

  btnReiniciar.addEventListener("click", async function () {
    limpiarCapasRuta();
    limpiarCapasDatos();
    limpiarResumen();

    origenInput.value = "";
    destinoInput.value = "";
    origenTuristico.value = "";
    destinoTuristico.value = "";
    origenTipo.value = "colonia";
    destinoTipo.value = "colonia";

    actualizarCamposSegunTipo();
    map.setView([20.6736, -103.3440], 11);

    await cargarColonias();
  });

  municipioSelect.addEventListener("change", async function () {
    limpiarCapasRuta();
    limpiarResumen();

    origenInput.value = "";
    destinoInput.value = "";
    origenTuristico.value = "";
    destinoTuristico.value = "";

    await cargarColonias();
  });

  toggleHex.addEventListener("change", () => renderHexGrid(coloniasActuales));
  togglePuntos.addEventListener("change", () => renderPuntos(coloniasActuales));
  toggleTurismo.addEventListener("change", async () => {
    await cargarZonasTuristicas();
  });

  toggleCamaras.addEventListener("change", function () {
    if (!toggleCamaras.checked) {
      camarasLayer.clearLayers();
    }
  });

  origenTipo.addEventListener("change", function () {
    actualizarCamposSegunTipo();

    if (origenTipo.value === "turistico" && origenTuristico.value !== "") {
      const punto = puntosTuristicos[Number(origenTuristico.value)];
      if (punto) zoomAPunto(punto.lat, punto.lon, `Origen turístico: ${punto.nombre}`);
    }
  });

  destinoTipo.addEventListener("change", function () {
    actualizarCamposSegunTipo();

    if (destinoTipo.value === "turistico" && destinoTuristico.value !== "") {
      const punto = puntosTuristicos[Number(destinoTuristico.value)];
      if (punto) zoomAPunto(punto.lat, punto.lon, `Destino turístico: ${punto.nombre}`);
    }
  });

  origenTuristico.addEventListener("change", function () {
    if (origenTipo.value !== "turistico") return;
    const idx = origenTuristico.value;
    if (idx === "") return;

    const punto = puntosTuristicos[Number(idx)];
    if (!punto) return;

    zoomAPunto(punto.lat, punto.lon, `Origen turístico: ${punto.nombre}`);
  });

  destinoTuristico.addEventListener("change", function () {
    if (destinoTipo.value !== "turistico") return;
    const idx = destinoTuristico.value;
    if (idx === "") return;

    const punto = puntosTuristicos[Number(idx)];
    if (!punto) return;

    zoomAPunto(punto.lat, punto.lon, `Destino turístico: ${punto.nombre}`);
  });

  origenInput.addEventListener("change", function () {
    if (origenTipo.value !== "colonia") return;
    manejarCambioColonia(origenInput, "Origen");
  });

  destinoInput.addEventListener("change", function () {
    if (destinoTipo.value !== "colonia") return;
    manejarCambioColonia(destinoInput, "Destino");
  });

  actualizarCamposSegunTipo();
  limpiarResumen();
  await cargarPuntosTuristicos();
  await cargarColonias();
});