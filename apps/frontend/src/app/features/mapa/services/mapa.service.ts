import { API_ROUTES } from "../../../config/api";
import type {
  MapaCamara,
  ZonaRiesgoMapa,
  PuntoOrigenIA,
  RespuestaRutaProbableAtacante,
} from "../types/mapa.types";

export async function calcularRutaProbableAtacante(
  origen: PuntoOrigenIA
): Promise<RespuestaRutaProbableAtacante> {
  const response = await fetch(API_ROUTES.iaRutaProbableDesplazamiento, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      origen,
      guardar: false,
    }),
  });

  if (!response.ok) {
    throw new Error("No se pudieron calcular las rutas probables del atacante");
  }

  return response.json();
}

export async function obtenerZonasMapa(): Promise<ZonaRiesgoMapa[]> {
  const response = await fetch(API_ROUTES.mapaZonas);

  if (!response.ok) {
    throw new Error("No se pudieron obtener las zonas del mapa");
  }

  return response.json();
}

export async function buscarZonaMapa(
  nombre: string
): Promise<ZonaRiesgoMapa | null> {
  const response = await fetch(API_ROUTES.mapaBuscarZona(nombre));

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error("No se pudo buscar la zona");
  }

  return response.json();
}

export async function obtenerCamarasMapa(): Promise<MapaCamara[]> {
  const response = await fetch(API_ROUTES.mapaCamaras);

  if (!response.ok) {
    return [];
  }

  return response.json();
}