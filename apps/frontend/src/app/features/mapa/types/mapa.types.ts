export type NivelRiesgo = "alto" | "medio" | "bajo" | "desconocido";

export type ZonaRiesgoMapa = {
  id: string;
  nombre: string;
  latitud: number;
  longitud: number;
  riesgo: number;
  nivel_riesgo: NivelRiesgo;
  color: "red" | "orange" | "green";
  radio: number;
};

export type MapaCamara = {
  id: string;
  nombre: string;
  zona?: string;
  activa: boolean;
  latitud: number;
  longitud: number;
};

export type PuntoMapa = {
  lat: number;
  lng: number;
};

export type InstruccionRutaEscape = {
  texto: string;
};

export type RutaEscapeMapa = {
  id: number;
  color: string;
  distancia: number;
  duracion: number;
  instrucciones: InstruccionRutaEscape[];
};