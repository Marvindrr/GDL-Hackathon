export const API_ROUTES = {
  camaras: "/api/camaras",
  eventosCamaras: "/api/camaras/eventos",
  filtrosDeteccion: "/api/camaras/filtros-deteccion",

  streamVivo: (camaraId: string) =>
    `/api/camaras/${camaraId}/stream-vivo`,

  ultimoFrame: (camaraId: string) =>
    `/api/camaras/${camaraId}/ultimo-frame`,

  mapaZonas: "/api/mapa/zonas",

  mapaBuscarZona: (nombre: string) =>
    `/api/mapa/buscar-zona?nombre=${encodeURIComponent(nombre)}`,

  mapaCamaras: "/api/mapa/camaras",

  gdlTurismo: "/gdl-turismo/",
};