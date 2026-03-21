document.addEventListener("DOMContentLoaded", async function () {
  const map = L.map("map").setView([20.6736, -103.3440], 12);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
  }).addTo(map);

  const municipioSelect = document.getElementById("municipio");
  const btnRecargar = document.getElementById("btnRecargar");
  const toggleHex = document.getElementById("toggleHex");
  const togglePuntos = document.getElementById("togglePuntos");

  const hexLayer = L.geoJSON(null).addTo(map);
  const puntosLayer = L.featureGroup().addTo(map);

  let coloniasActuales = [];

  function getColorByRisk(riesgo) {
    if (riesgo === null || riesgo === undefined) return "#9ca3af";
    if (riesgo <= 25) return "#22c55e";
    if (riesgo <= 50) return "#eab308";
    if (riesgo <= 75) return "#f97316";
    return "#ef4444";
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
    const cellSide = 0.45;

    const grid = turf.hexGrid(bbox, cellSide, { units: "kilometers" });

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

      const hexCercanos = hexOrdenados.slice(0, 7);

      hexCercanos.forEach(item => {
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
        color: "#ffffff",
        weight: 1.5,
        fillColor: getColorByRisk(colonia.riesgo),
        fillOpacity: 1
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
    hexLayer.clearLayers();
    puntosLayer.clearLayers();
    renderColonias();

    if (hexLayer.getBounds().isValid()) {
      map.fitBounds(hexLayer.getBounds(), { padding: [30, 30] });
    } else if (puntosLayer.getBounds().isValid()) {
      map.fitBounds(puntosLayer.getBounds(), { padding: [30, 30] });
    }
  }

  btnRecargar.addEventListener("click", cargarColonias);
  municipioSelect.addEventListener("change", cargarColonias);
  toggleHex.addEventListener("change", renderColonias);
  togglePuntos.addEventListener("change", renderColonias);

  await cargarColonias();
});