import { API_ROUTES } from "../config/api";
import type { Camara, EventoCamara, FiltrosDeteccion } from "../types/camaras.types";

export async function obtenerCamaras(): Promise<Camara[]> {
  const response = await fetch(API_ROUTES.camaras);

  if (!response.ok) {
    throw new Error("No se pudieron obtener las cámaras");
  }

  return response.json();
}

export async function obtenerEventosCamaras(): Promise<EventoCamara[]> {
  const response = await fetch(API_ROUTES.eventosCamaras);

  if (!response.ok) {
    throw new Error("No se pudieron obtener los eventos de cámaras");
  }

  return response.json();
}

export async function obtenerFiltrosDeteccion(): Promise<FiltrosDeteccion> {
  const response = await fetch(API_ROUTES.filtrosDeteccion);

  if (!response.ok) {
    throw new Error("No se pudieron obtener los filtros de detección");
  }

  return response.json();
}

export async function actualizarFiltrosDeteccion(
  filtros: FiltrosDeteccion
): Promise<FiltrosDeteccion> {
  const response = await fetch(API_ROUTES.filtrosDeteccion, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(filtros),
  });

  if (!response.ok) {
    throw new Error("No se pudieron actualizar los filtros de detección");
  }

  const data = await response.json();

  return data.filtros;
}