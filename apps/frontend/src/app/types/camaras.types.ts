export type Camara = {
  id: string;
  nombre: string;
  activa: boolean;
  zona?: string;
  latitud?: number;
  longitud?: number;
};

export type RopaDetectada = {
  superior?: {
    tipo: string;
    color: string;
    confianza_color: number;
  };
  inferior?: {
    tipo: string;
    color: string;
    confianza_color: number;
  };
};

export type Deteccion = {
  clase: string;
  confianza: number;
  ropa?: RopaDetectada;
};

export type EventoCamara = {
  camara_id: string;
  nombre: string;
  zona?: string;
  timestamp: number;
  detecciones: Deteccion[];
  frame_url: string;
  stream_url: string;
  latitud?: number;
  longitud?: number;
};

export type TipoRopaFiltro = "cualquiera" | "superior" | "inferior";

export type ColorRopaFiltro =
  | "cualquiera"
  | "rojo"
  | "naranja"
  | "amarillo"
  | "verde"
  | "azul"
  | "morado"
  | "rosa"
  | "negro"
  | "blanco"
  | "gris";

export type FiltrosDeteccion = {
  activo: boolean;
  tipo_ropa: TipoRopaFiltro;
  color_ropa: ColorRopaFiltro;
  confianza_color_minima: number;
};

