document.addEventListener("DOMContentLoaded", async function () {
  const map = L.map("map").setView([20.6767, -103.3475], 12);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  const municipioSelect = document.getElementById("municipio");
  const btnCalcular = document.getElementById("btnCalcular");
  const btnReiniciar = document.getElementById("btnReiniciar");

  const origenInput = document.getElementById("origen");
  const destinoInput = document.getElementById("destino");

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
  const turismoLayer = L.featureGroup().addTo(map);

  let coloniasActuales = [];

  function getColorByRisk(riesgo) {
    if (riesgo === null || riesgo === undefined) return "#9ca3af"; // gris
    if (riesgo <= 25) return "#22c55e";
    if (riesgo <= 50) return "#f59e0b";
    if (riesgo <= 75) return "#ef4444";
    return "#7f1d1d";
  }

  function limpiarResumen() {
    riesgoRuta.textContent = "--";
    distanciaRuta.textContent = "--";
    tiempoRuta.textContent = "--";
    camarasRuta.textContent = "--";
    coloniasCriticas.textContent = "--";
  }

  function limpiarRuta() {
    rutaLayer.clearLayers();
    camarasLayer.clearLayers();
    turismoLayer.clearLayers();
  }

  function limpiarVisualizacionColonias() {
    hexLayer.clearLayers();
    puntosLayer.clearLayers();
  }

  function calcularBBox(colonias) {
    const lats = colonias.map(c => c.lat);
    const lons = colonias.map(c => c.lon);

    const margen = 0.01;

    return [
      Math.min(...lons) - margen,
      Math.min(...lats) - margen,
      Math.max(...lons) + margen,
      Math.max(...lats) + margen
    ];
  }

  function distanciaEnKm(lat1, lon1, lat2, lon2) {
    const from = turf.point([lon1, lat1]);
    const to = turf.point([lon2, lat2]);
    return turf.distance(from, to, { units: "kilometers" });
  }

  function generarHexGrid(colonias) {
    const bbox = calcularBBox(colonias);
    const cellSide = 0.45; // prueba 0.35 o 0.50 si quieres más/menos detalle

    const grid = turf.hexGrid(bbox, cellSide, { units: "kilometers" });

    // Todo empieza en gris
    grid.features.forEach((feature, index) => {
      feature.properties = {
        id: index + 1,
        riesgo: null,
        colonia_ref: "Sin dato",
        municipio: "",
        distancia_ref_km: Infinity
      };
    });

    colonias.forEach(colonia => {
      const hexOrdenados = grid.features
        .map(feature => {
          const centro = turf.centroid(feature);
          const [lon, lat] = centro.geometry.coordinates;

          return {
            feature,
            distancia: distanciaEnKm(lat, lon, colonia.lat, colonia.lon)
          };
        })
        .sort((a, b) => a.distancia - b.distancia);

      // 7 más cercanos = aprox centro + 6 alrededor
      // Si lo quieres más estricto, cambia 7 por 6 o 5
      const hexCercanos = hexOrdenados.slice(0, 7);

      hexCercanos.forEach(item => {
        const actual = item.feature.properties.distancia_ref_km ?? Infinity;

        // Solo actualiza si esta colonia está más cerca que la que ya tenía el hex
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

    if (!toggleHex.checked || !colonias.length) return;

    const grid = generarHexGrid(colonias);
    hexLayer.addData(grid);

    hexLayer.eachLayer(layer => {
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
        <strong>Hexágono de riesgo</strong><br>
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

  function renderColonias() {
    renderHexGrid(coloniasActuales);
    renderPuntos(coloniasActuales);
  }

  async function cargarColonias() {
    const municipio = municipioSelect.value;

    const response = await fetch(`/api/colonias?municipio=${encodeURIComponent(municipio)}`);
    const data = await response.json();

    coloniasActuales = data;
    limpiarVisualizacionColonias();
    renderColonias();

    if (hexLayer.getBounds().isValid()) {
      map.fitBounds(hexLayer.getBounds(), { padding: [20, 20] });
    } else if (puntosLayer.getBounds().isValid()) {
      map.fitBounds(puntosLayer.getBounds(), { padding: [20, 20] });
    }
  }

  function buscarColoniaPorNombre(nombre) {
    const texto = nombre.trim().toLowerCase();
    return coloniasActuales.find((c) =>
      c.nombre_colonia.toLowerCase().includes(texto)
    );
  }

  function renderCamarasDemo(origenColonia, destinoColonia) {
    camarasLayer.clearLayers();

    if (!toggleCamaras.checked) return 0;

    const camarasDemo = [
      { id: 1, lat: origenColonia.lat + 0.004, lon: origenColonia.lon + 0.004 },
      { id: 2, lat: destinoColonia.lat - 0.003, lon: destinoColonia.lon - 0.003 }
    ];

    camarasDemo.forEach((camara) => {
      L.marker([camara.lat, camara.lon])
        .bindPopup(`Cámara ${camara.id}`)
        .addTo(camarasLayer);
    });

    return camarasDemo.length;
  }

  function renderTurismoDemo() {
    turismoLayer.clearLayers();

    if (!toggleTurismo.checked) return;

    const poligonoDemo = [
      [20.6795, -103.3515],
      [20.6795, -103.3435],
      [20.6745, -103.3435],
      [20.6745, -103.3515]
    ];

    L.polygon(poligonoDemo, {
      color: "gold",
      fillColor: "gold",
      fillOpacity: 0.2
    })
      .bindPopup("Zona turística demo")
      .addTo(turismoLayer);
  }

  btnCalcular.addEventListener("click", async function () {
    const origen = origenInput.value.trim();
    const destino = destinoInput.value.trim();
    const municipio = municipioSelect.value;
    const tipoRuta = document.querySelector('input[name="tipoRuta"]:checked')?.value || "segura";

    if (!origen || !destino) {
      alert("Ingresa origen y destino");
      return;
    }

    const origenColonia = buscarColoniaPorNombre(origen);
    const destinoColonia = buscarColoniaPorNombre(destino);

    if (!origenColonia || !destinoColonia) {
      alert("No se encontró el origen o el destino en las colonias cargadas");
      return;
    }

    const response = await fetch("/api/ruta", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        origen,
        destino,
        municipio,
        tipo_ruta: tipoRuta
      })
    });

    const data = await response.json();

    limpiarRuta();

    const puntosRuta = [
      [origenColonia.lat, origenColonia.lon],
      ...(data.ruta || []),
      [destinoColonia.lat, destinoColonia.lon]
    ];

    const polyline = L.polyline(puntosRuta, {
      color: tipoRuta === "segura" ? "blue" : "purple",
      weight: 5
    }).addTo(rutaLayer);

    L.marker([origenColonia.lat, origenColonia.lon])
      .bindPopup(`Origen: ${origenColonia.nombre_colonia}`)
      .addTo(rutaLayer);

    L.marker([destinoColonia.lat, destinoColonia.lon])
      .bindPopup(`Destino: ${destinoColonia.nombre_colonia}`)
      .addTo(rutaLayer);

    const totalCamaras = renderCamarasDemo(origenColonia, destinoColonia);
    renderTurismoDemo();

    riesgoRuta.textContent = data.riesgo_total ?? "--";
    distanciaRuta.textContent = data.distancia ?? "--";
    tiempoRuta.textContent = data.tiempo ?? "--";
    camarasRuta.textContent = totalCamaras || data.camaras_cercanas || "--";
    coloniasCriticas.textContent = (data.colonias_criticas || []).join(", ") || "--";

    map.fitBounds(polyline.getBounds(), { padding: [30, 30] });
  });

  btnReiniciar.addEventListener("click", async function () {
    limpiarVisualizacionColonias();
    limpiarRuta();
    limpiarResumen();

    origenInput.value = "";
    destinoInput.value = "";

    map.setView([20.6767, -103.3475], 12);
    await cargarColonias();
  });

  municipioSelect.addEventListener("change", async function () {
    limpiarRuta();
    limpiarResumen();
    await cargarColonias();
  });

  toggleHex.addEventListener("change", renderColonias);
  togglePuntos.addEventListener("change", renderColonias);

  toggleCamaras.addEventListener("change", function () {
    if (!toggleCamaras.checked) {
      camarasLayer.clearLayers();
    }
  });

  toggleTurismo.addEventListener("change", function () {
    if (!toggleTurismo.checked) {
      turismoLayer.clearLayers();
    }
  });

  limpiarResumen();
  await cargarColonias();
});