document.addEventListener("DOMContentLoaded", function () {
  const socket = io();

  const map = L.map("map", {
    center: [20.677, -103.3765],
    zoom: 12,
    zoomControl: false
  });

  const mapaClaro = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap"
  });

  const mapaSatelital = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    { attribution: "Esri World Imagery" }
  );

  mapaClaro.addTo(map);
  L.control.zoom({ position: "bottomright" }).addTo(map);
  L.control.layers(
    { "Mapa claro": mapaClaro, "Satelital": mapaSatelital },
    null,
    { position: "topright" }
  ).addTo(map);

  const attractions = [
    {
      id: 1,
      nombre: "Catedral de Guadalajara",
      lat: 20.6772,
      lng: -103.3469,
      iconClass: "fa-solid fa-church",
      zona: "Centro Historico",
      categoria: "turistico",
      imagen: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQGnvoKkuf5ruw_srfqBDEd67JeL9b4A_tcWA&s",
      info: "Corazon de la identidad tapatia. Sus torres neogoticas y su plaza central la vuelven un punto clave para visitantes y aficionados."
    },
    {
      id: 2,
      nombre: "Teatro Degollado",
      lat: 20.6779,
      lng: -103.3444,
      iconClass: "fa-solid fa-masks-theater",
      zona: "Centro Historico",
      categoria: "turistico",
      imagen: "https://image-tc.galaxy.tf/wijpeg-2p8lc3uabccmrbg6t39rce5sa/teatro-degollado.jpg",
      info: "Joya neoclasica de Guadalajara, ideal para conectar la experiencia mundialista con cultura, musica y recorridos por el centro."
    },
    {
      id: 3,
      nombre: "Hospicio Cabanas",
      lat: 20.6769,
      lng: -103.3374,
      iconClass: "fa-solid fa-landmark",
      zona: "Centro Historico",
      categoria: "turistico",
      imagen: "https://image-tc.galaxy.tf/wijpeg-dudtaen3w3x9b30o8nm17ktom/city-center-hospicio-cabanas_standard.jpg?crop=92%2C0%2C1616%2C1212&width=1400",
      info: "Patrimonio de la Humanidad por la UNESCO y uno de los puntos culturales mas potentes para rutas de turismo urbano."
    },
    {
      id: 4,
      nombre: "Mercado San Juan de Dios",
      lat: 20.6748,
      lng: -103.3392,
      iconClass: "fa-solid fa-store",
      zona: "Centro Historico",
      categoria: "turistico",
      imagen: "https://upload.wikimedia.org/wikipedia/commons/a/ab/Mercado_san_juan_de_dios_guadalajara_interior.jpg",
      info: "Mercado historico de gran escala con artesanias, comida local y flujo constante de visitantes nacionales e internacionales."
    },
    {
      id: 5,
      nombre: "Templo Expiatorio",
      lat: 20.6723,
      lng: -103.3562,
      iconClass: "fa-solid fa-church",
      zona: "Juarez / Centro",
      categoria: "turistico",
      imagen: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRW1jWq7iqvfqNqfpu-kTZ-jt9jIiB4r7GUNQ&s",
      info: "Punto arquitectonico de referencia en la zona Centro-Juarez, util para rutas peatonales y recorridos culturales."
    },
    {
      id: 6,
      nombre: "Tlaquepaque Centro",
      lat: 20.6401,
      lng: -103.3115,
      iconClass: "fa-solid fa-palette",
      zona: "Tlaquepaque",
      categoria: "turistico",
      imagen: "https://img.chilango.com/cdn-cgi/image/width=1200,height=675,quality=75,format=auto,onerror=redirect/2025/06/tlaquepaque-guadalajara-jalisco.jpg",
      info: "Distrito artesanal y gastronomico con mariachi, galerias y recorridos de alto interes para visitantes."
    },
    {
      id: 7,
      nombre: "Estadio Akron",
      lat: 20.6817,
      lng: -103.4626,
      iconClass: "fa-solid fa-futbol",
      zona: "Zapopan Oeste",
      categoria: "futbol",
      imagen: "https://www.informador.mx/__export/1659253245091/sites/elinformador/img/2022/07/31/imagen_imagen_fy7x0t2xgae4kol_-_cmyk_x3x_crop1659253223146.jpg_1902800913.jpg",
      info: "Sede oficial de la Copa Mundial FIFA 2026 en Guadalajara y nodo principal de movilidad durante dias de partido."
    },
    {
      id: 8,
      nombre: "Verde Valle",
      lat: 20.6625,
      lng: -103.4219,
      iconClass: "fa-solid fa-person-running",
      zona: "Zapopan",
      categoria: "futbol",
      imagen: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQIcOi5CjB4uPi4YdfsaRlQitfpM4U_JTZaNg&s",
      info: "Centro de entrenamiento ligado a Chivas, clave para operaciones deportivas y traslados controlados."
    },
    {
      id: 9,
      nombre: "Atlas Colomos",
      lat: 20.7042,
      lng: -103.3912,
      iconClass: "fa-solid fa-shoe-prints",
      zona: "Providencia / Colomos",
      categoria: "futbol",
      imagen: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRCvu2SgMJtafQQDe53lFSBYZyvSIeyqKDoIw&s",
      info: "Zona deportiva al norte de la ciudad, cercana a corredores hoteleros y areas verdes."
    },
    {
      id: 10,
      nombre: "Centro Comercial Andares",
      lat: 20.7104,
      lng: -103.4115,
      iconClass: "fa-solid fa-bag-shopping",
      zona: "Zona Real",
      categoria: "comercial",
      imagen: "https://images.squarespace-cdn.com/content/v1/60df5f2f019094235e597bb4/1632749752981-7NKBLJL6LNFV5I6IT51P/Lorena+Darquea-Paseo+Andares-15+%281%29.jpg",
      info: "Complejo comercial premium con alta afluencia, restaurantes y puntos de encuentro para visitantes."
    },
    {
      id: 11,
      nombre: "Galerias Guadalajara",
      lat: 20.6782,
      lng: -103.4331,
      iconClass: "fa-solid fa-cart-shopping",
      zona: "Rafael Sanzio / Vallarta",
      categoria: "comercial",
      imagen: "https://galeriasgdl.mx/wp-content/uploads/2023/06/2.jpg",
      info: "Plaza comercial amplia al poniente, conectada con avenidas principales y servicios urbanos."
    },
    {
      id: 12,
      nombre: "Plaza Patria",
      lat: 20.7162,
      lng: -103.3768,
      iconClass: "fa-solid fa-building",
      zona: "Avila Camacho / Zapopan",
      categoria: "comercial",
      imagen: "https://plazapatria.com/contenido/uploads/2020/07/grid-plaza-patria-new-section.jpg",
      info: "Plaza tradicional remodelada, con conexion cercana a transporte masivo y corredores de Zapopan."
    }
  ];

  const categoryLabels = {
    futbol: "Sede FIFA",
    turistico: "Cultura y arte",
    comercial: "Shopping"
  };

  const categoryColors = {
    futbol: "#a855f7",
    turistico: "#10b981",
    comercial: "#06b6d4",
    riesgo: "#f43f5e",
    busqueda: "#f59e0b"
  };

  let currentMarker = null;
  let selectedPlace = null;
  let landmarkMarkers = [];
  let searchMarkers = [];
  let riskLayers = [];
  let routeControls = [];
  let routeLayers = [];
  let cameraMarkers = [];
  let userMarker = null;

  const searchInput = document.getElementById("search_input");
  const searchResults = document.getElementById("search_results");
  const showRiskButton = document.getElementById("show_risk_areas_button");
  const routeButton = document.getElementById("route_button");
  const directionsPanel = document.getElementById("directions_panel");
  const directionsBody = directionsPanel
    ? directionsPanel.querySelector(".directions-body")
    : null;

  const placeModal = document.getElementById("info-modal-centro");
  const fifaModal = document.getElementById("fifa-modal");
  const modalImage = document.getElementById("modal-img");
  const modalBadge = document.getElementById("modal-badge");
  const modalTitle = document.getElementById("modal-title");
  const modalDesc = document.getElementById("modal-desc");

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function clearLayerList(list) {
    list.forEach((layer) => {
      if (layer && map.hasLayer(layer)) {
        map.removeLayer(layer);
      }
    });
    list.length = 0;
  }

  function clearRoutes() {
    routeControls.forEach((control) => {
      try {
        map.removeControl(control);
      } catch (error) {
        console.warn("No se pudo retirar un control de ruta", error);
      }
    });
    routeControls = [];
    clearLayerList(routeLayers);
    clearLayerList(cameraMarkers);
  }

  function resetDirections(message) {
    if (!directionsBody) return;
    directionsBody.innerHTML = escapeHtml(message || "Selecciona un pin o una colonia para calcular ruta.");
  }

  function riskColor(riesgo) {
    const value = Number(riesgo);
    if (Number.isNaN(value)) return "#94a3b8";
    if (value <= 25) return "#22c55e";
    if (value <= 50) return "#eab308";
    if (value <= 75) return "#f97316";
    return "#ef4444";
  }

  function riskText(riesgo) {
    const value = Number(riesgo);
    if (Number.isNaN(value)) return "S/D";
    if (value <= 25) return "Bajo";
    if (value <= 50) return "Moderado";
    if (value <= 75) return "Alto";
    return "Muy alto";
  }

  function makeIcon(type, iconClass) {
    const className = type || "turistico";
    const safeIcon = iconClass || "fa-solid fa-location-dot";

    return L.divIcon({
      className: "",
      html: `<div class="legacy-pin ${className}"><i class="${safeIcon}"></i></div>`,
      iconSize: [52, 52],
      iconAnchor: [26, 26],
      popupAnchor: [0, -22]
    });
  }

  function fitLayers(layers, padding) {
    const validLayers = layers.filter(Boolean);
    if (!validLayers.length) return;

    const group = L.featureGroup(validLayers);
    if (group.getBounds().isValid()) {
      map.fitBounds(group.getBounds().pad(padding || 0.18));
    }
  }

  function renderLandmarks(category) {
    clearLayerList(landmarkMarkers);

    const items = category && category !== "all"
      ? attractions.filter((place) => place.categoria === category)
      : attractions;

    items.forEach((place) => {
      const marker = L.marker([place.lat, place.lng], {
        icon: makeIcon(place.categoria, place.iconClass)
      })
        .addTo(map)
        .bindPopup(`
          <strong>${escapeHtml(place.nombre)}</strong><br>
          ${escapeHtml(place.zona)}<br>
          <button class="popup-button" type="button">Ver detalle</button>
        `);

      marker.on("click", () => openPlaceModal(place));
      landmarkMarkers.push(marker);
    });

    if (category && category !== "all") {
      fitLayers(landmarkMarkers, 0.25);
    }
  }

  function setActiveCategory(button) {
    document.querySelectorAll(".category-card").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
  }

  function openPlaceModal(place) {
    selectedPlace = place;
    modalImage.src = place.imagen;
    modalImage.alt = place.nombre;
    modalBadge.textContent = categoryLabels[place.categoria] || "Punto GDL";
    modalBadge.style.background = categoryColors[place.categoria] || "#10b981";
    modalTitle.textContent = place.nombre;
    modalDesc.textContent = place.info;
    placeModal.classList.remove("hidden");
  }

  function closePlaceModal() {
    placeModal.classList.add("hidden");
  }

  function setCurrentPoint(lat, lng, label, riskValue) {
    clearLayerList(searchMarkers);
    clearRoutes();
    resetDirections(`Punto seleccionado: ${label}. Ya puedes calcular rutas.`);

    const marker = L.marker([lat, lng], {
      icon: makeIcon("search", "fa-solid fa-location-crosshairs")
    })
      .addTo(map)
      .bindPopup(`
        <strong>${escapeHtml(label)}</strong><br>
        ${riskValue !== undefined ? `Riesgo: ${escapeHtml(riskValue)}%` : "Punto seleccionado"}
      `)
      .openPopup();

    marker.latlng = [lat, lng];
    currentMarker = marker;
    searchMarkers.push(marker);
    routeButton.disabled = false;
    map.flyTo([lat, lng], 15, { duration: 0.8 });
  }

  function setCurrentPlace(place) {
    closePlaceModal();
    setCurrentPoint(place.lat, place.lng, place.nombre);
  }

  function renderSearchResults(results) {
    searchResults.innerHTML = "";

    if (!results || results.length === 0) {
      searchResults.innerHTML = "<p>No se encontraron colonias.</p>";
      return;
    }

    results.slice(0, 20).forEach((colonia) => {
      const button = document.createElement("button");
      const lat = colonia.centro?.[1];
      const lng = colonia.centro?.[0];
      const riesgo = colonia.riesgo;
      const color = riskColor(riesgo);

      button.type = "button";
      button.className = "result-item";
      button.innerHTML = `
        <span>
          <strong>${escapeHtml(colonia.nombre_colonia)}</strong>
          <span>Riesgo ${escapeHtml(riskText(riesgo))}</span>
        </span>
        <b class="risk-pill" style="background:${color}">${escapeHtml(riesgo)}%</b>
      `;

      button.addEventListener("click", () => {
        if (typeof lat === "number" && typeof lng === "number") {
          setCurrentPoint(lat, lng, colonia.nombre_colonia, riesgo);
        }
      });

      searchResults.appendChild(button);
    });
  }

  function renderDirections(routeIndex, color, instructions) {
    if (!directionsBody) return;
    if (routeIndex === 1) directionsBody.innerHTML = "";

    const title = document.createElement("div");
    title.className = "direction-route-title";
    title.style.color = color;
    title.textContent = `Ruta ${routeIndex}`;
    directionsBody.appendChild(title);

    if (!instructions || instructions.length === 0) {
      const step = document.createElement("div");
      step.className = "direction-step";
      step.textContent = "Ruta directa sugerida mientras el servicio externo responde.";
      directionsBody.appendChild(step);
      return;
    }

    instructions.slice(0, 8).forEach((instruction) => {
      const step = document.createElement("div");
      step.className = "direction-step";
      step.textContent = instruction.text || instruction;
      directionsBody.appendChild(step);
    });
  }

  function drawFallbackRoute(origin, destination, routeIndex, color) {
    const line = L.polyline(
      [
        [origin.lat, origin.lng],
        [destination.lat, destination.lng]
      ],
      { color, weight: 4, opacity: 0.82, dashArray: "8 8" }
    ).addTo(map);

    routeLayers.push(line);
    renderDirections(routeIndex, color, []);
  }

  function generateRoute(origin, destination, routeIndex) {
    const colors = ["#10b981", "#f43f5e", "#06b6d4", "#f59e0b"];
    const color = colors[(routeIndex - 1) % colors.length];

    if (!L.Routing) {
      drawFallbackRoute(origin, destination, routeIndex, color);
      return;
    }

    const control = L.Routing.control({
      waypoints: [
        L.latLng(origin.lat, origin.lng),
        L.latLng(destination.lat, destination.lng)
      ],
      addWaypoints: false,
      draggableWaypoints: false,
      fitSelectedRoutes: routeIndex === 1,
      show: false,
      createMarker: function () {
        return null;
      },
      lineOptions: {
        styles: [{ color, weight: 6, opacity: 0.86 }]
      }
    }).addTo(map);

    routeControls.push(control);

    const container = control.getContainer();
    if (container) container.style.display = "none";

    control.on("routesfound", function (event) {
      const route = event.routes[0];
      const summary = route.summary || {};

      socket.emit("ruta_cambiada", {
        distancia: summary.totalDistance,
        duracion: summary.totalTime,
        waypoints: route.coordinates
      });

      renderDirections(routeIndex, color, route.instructions || []);
    });

    control.on("routingerror", function () {
      drawFallbackRoute(origin, destination, routeIndex, color);
    });
  }

  function calculateRoutesFromCurrentPoint() {
    if (!currentMarker) {
      resetDirections("Selecciona primero una colonia o un punto del mapa.");
      return;
    }

    const selected = currentMarker.getLatLng();
    const origin = { lat: selected.lat, lng: selected.lng };

    clearRoutes();
    resetDirections("Calculando rutas...");

    const safetyCircle = L.circle([origin.lat, origin.lng], {
      color: "#f43f5e",
      fillColor: "#f43f5e",
      fillOpacity: 0.13,
      radius: 1000,
      weight: 2
    }).addTo(map);
    routeLayers.push(safetyCircle);

    socket.emit("enviar_coordenadas", { lat: origin.lat, lng: origin.lng });

    const destinations = [
      { lat: origin.lat + 0.012, lng: origin.lng + 0.012 },
      { lat: origin.lat - 0.012, lng: origin.lng - 0.012 },
      { lat: origin.lat + 0.012, lng: origin.lng - 0.012 },
      { lat: origin.lat - 0.012, lng: origin.lng + 0.012 }
    ];

    destinations.forEach((destination, index) => {
      generateRoute(origin, destination, index + 1);
    });
  }

  function renderRiskZones(zones) {
    clearLayerList(riskLayers);

    zones.forEach((zona) => {
      const color = riskColor(zona.riesgo);

      const circle = L.circle([zona.lat, zona.lng], {
        color,
        radius: 500,
        fillColor: color,
        fillOpacity: 0.26,
        weight: 2
      }).addTo(map);

      const marker = L.circleMarker([zona.lat, zona.lng], {
        radius: 5,
        color: "#071018",
        fillColor: color,
        fillOpacity: 1,
        weight: 1
      })
        .addTo(map)
        .bindPopup(`<strong>${escapeHtml(zona.nombre)}</strong><br>Riesgo: ${escapeHtml(zona.riesgo)}%`);

      riskLayers.push(circle, marker);
    });

    fitLayers(riskLayers, 0.1);
  }

  function renderCameraMarkers(cameras) {
    clearLayerList(cameraMarkers);

    (cameras || []).forEach((camera) => {
      if (camera.lat === undefined || camera.lon === undefined) return;

      const marker = L.marker([camera.lat, camera.lon], {
        icon: makeIcon("risk", "fa-solid fa-video")
      })
        .addTo(map)
        .bindPopup(`<strong>Camara ${escapeHtml(camera.id || "")}</strong>`);

      cameraMarkers.push(marker);
    });
  }

  searchInput.addEventListener("input", function () {
    const query = searchInput.value.trim();

    if (query.length < 2) {
      searchResults.innerHTML = "<p>Escribe al menos dos caracteres.</p>";
      return;
    }

    socket.emit("search", query);
  });

  showRiskButton.addEventListener("click", function () {
    resetDirections("Cargando zonas de riesgo...");
    socket.emit("mostrar_zonas_riesgo");
  });

  routeButton.addEventListener("click", calculateRoutesFromCurrentPoint);

  document.querySelectorAll(".category-card").forEach((button) => {
    button.addEventListener("click", function () {
      setActiveCategory(button);
      renderLandmarks(button.dataset.filter);
    });
  });

  document.getElementById("modal-close-button").addEventListener("click", closePlaceModal);
  document.getElementById("modal-explore-button").addEventListener("click", closePlaceModal);
  document.getElementById("modal-route-button").addEventListener("click", function () {
    if (selectedPlace) setCurrentPlace(selectedPlace);
    calculateRoutesFromCurrentPoint();
  });

  document.getElementById("open-fifa-modal").addEventListener("click", function () {
    fifaModal.classList.remove("hidden");
  });

  document.getElementById("close-fifa-modal").addEventListener("click", function () {
    fifaModal.classList.add("hidden");
  });

  [placeModal, fifaModal].forEach((modal) => {
    modal.addEventListener("click", function (event) {
      if (event.target === modal) {
        modal.classList.add("hidden");
      }
    });
  });

  socket.on("search_results", renderSearchResults);
  socket.on("zonas_riesgo", renderRiskZones);
  socket.on("camaras_cercanas", renderCameraMarkers);

  map.locate({ setView: false, watch: true, enableHighAccuracy: true });
  map.on("locationfound", function (event) {
    if (!userMarker) {
      userMarker = L.circleMarker(event.latlng, {
        radius: 8,
        color: "#ffffff",
        fillColor: "#f43f5e",
        fillOpacity: 1,
        weight: 3
      })
        .addTo(map)
        .bindPopup("<strong>Tu ubicacion actual</strong>");
    } else {
      userMarker.setLatLng(event.latlng);
    }
  });

  renderLandmarks("all");
});
