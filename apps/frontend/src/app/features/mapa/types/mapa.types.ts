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

export type PuntoOrigenIA = {
  lat: number;
  lon: number;
};

export type CoordenadaGeoJson = [number, number];

export type RutaProbableAtacanteFeature = {
  type: "Feature";
  properties: {
    direccion?: string;
    distancia_m?: number;
    probabilidad_operativa?: number;
    riesgo_zonas?: number;
    tipo_ruta?: string;
    algoritmo?: string;
    color?: string;
    [key: string]: unknown;
  };
  geometry: {
    type: "LineString";
    coordinates: CoordenadaGeoJson[];
  };
};

export type CandidataRutaAtacante = {
  direccion: string;
  distancia_m: number;
  probabilidad_operativa: number;
  riesgo_zonas: number;
  destino_estimado?: {
    lat?: number;
    lon?: number;
  } | null;
};

export type RespuestaRutaProbableAtacante = {
  algoritmo: string;
  tipo_ruta: string;
  direccion_probable: string;
  distancia_m: number;
  probabilidad_operativa: number;
  riesgo_zonas: number;
  id_ruta?: number | null;
  candidatas: CandidataRutaAtacante[];
  geojson: {
    type: "FeatureCollection";
    features: RutaProbableAtacanteFeature[];
  };
};