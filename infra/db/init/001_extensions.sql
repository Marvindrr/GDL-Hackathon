CREATE EXTENSION IF NOT EXISTS postgis;
-- Más adelante, si agregamos pgRouting:
-- CREATE EXTENSION IF NOT EXISTS pgrouting;

CREATE TABLE municipios (
    id_municipio SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    estado VARCHAR(120) NOT NULL DEFAULT 'Jalisco',
    geom GEOMETRY(MULTIPOLYGON, 4326),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_municipios_geom
ON municipios
USING GIST (geom);

CREATE TABLE zonas (
    id_zona SERIAL PRIMARY KEY,
    id_municipio INT REFERENCES municipios(id_municipio),
    nombre VARCHAR(180) NOT NULL,
    tipo VARCHAR(50) DEFAULT 'colonia',

    riesgo_base NUMERIC(5,2) DEFAULT 0,
    reputacion NUMERIC(5,2) DEFAULT 50,
    nivel_luz NUMERIC(5,2) DEFAULT NULL,

    geom GEOMETRY(MULTIPOLYGON, 4326),
    centro GEOMETRY(POINT, 4326),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_zonas_geom
ON zonas
USING GIST (geom);

CREATE INDEX idx_zonas_centro
ON zonas
USING GIST (centro);

CREATE TABLE camaras (
    id_camara SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    codigo_externo VARCHAR(100),

    tipo VARCHAR(50) DEFAULT 'fija',
    fuente VARCHAR(80) DEFAULT 'simulada',

    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    ubicacion GEOMETRY(POINT, 4326) NOT NULL,

    direccion_texto TEXT,
    activa BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_camaras_ubicacion
ON camaras
USING GIST (ubicacion);

-- Preguntas para análisis
-- ¿Qué cámaras están cerca de esta detección?
-- ¿Qué cámara pertenece a qué colonia?
-- ¿Qué cámaras podrían ver la siguiente ruta?

CREATE TABLE calles_edges (
    id_edge SERIAL PRIMARY KEY,

    nombre VARCHAR(180),
    tipo_via VARCHAR(80),

    source BIGINT,
    target BIGINT,

    distancia_m DOUBLE PRECISION,
    velocidad_estimada_kmh DOUBLE PRECISION DEFAULT 30,

    riesgo_base NUMERIC(5,2) DEFAULT 0,
    costo_base DOUBLE PRECISION DEFAULT 1,

    geom GEOMETRY(LINESTRING, 4326) NOT NULL,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_calles_edges_geom
ON calles_edges
USING GIST (geom);

CREATE INDEX idx_calles_edges_source
ON calles_edges(source);

CREATE INDEX idx_calles_edges_target
ON calles_edges(target);

CREATE TABLE calles_nodes (
    id_node BIGSERIAL PRIMARY KEY,
    geom GEOMETRY(POINT, 4326) NOT NULL
);

CREATE INDEX idx_calles_nodes_geom
ON calles_nodes
USING GIST (geom);

CREATE TABLE puntos_turisticos (
    id_punto SERIAL PRIMARY KEY,
    nombre VARCHAR(180) NOT NULL,
    categoria VARCHAR(80),

    descripcion TEXT,

    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    ubicacion GEOMETRY(POINT, 4326) NOT NULL,

    activo BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_puntos_turisticos_ubicacion
ON puntos_turisticos
USING GIST (ubicacion);


CREATE TABLE reportes_seguridad (
    id_reporte SERIAL PRIMARY KEY,

    tipo_reporte VARCHAR(80) NOT NULL,
    descripcion TEXT,

    severidad INT DEFAULT 1,

    fuente VARCHAR(80) DEFAULT 'manual',
    fecha_reporte TIMESTAMP NOT NULL DEFAULT NOW(),

    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    ubicacion GEOMETRY(POINT, 4326) NOT NULL,

    validado BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reportes_ubicacion
ON reportes_seguridad
USING GIST (ubicacion);

CREATE INDEX idx_reportes_fecha
ON reportes_seguridad(fecha_reporte);

-- Tipos de reportes de seguridad
--robo
--asalto
--agresion
--zona_oscura
--aglomeracion
--vandalismo
--persona_sospechosa
--vehiculo_sospechoso


CREATE TABLE factores_riesgo_zona (
    id_factor SERIAL PRIMARY KEY,
    id_zona INT REFERENCES zonas(id_zona),

    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,

    reportes_score NUMERIC(5,2) DEFAULT 0,
    luz_score NUMERIC(5,2) DEFAULT 50,
    reputacion_score NUMERIC(5,2) DEFAULT 50,
    hora_score NUMERIC(5,2) DEFAULT 0,
    camaras_score NUMERIC(5,2) DEFAULT 50,
    flujo_personas_score NUMERIC(5,2) DEFAULT 50,

    riesgo_total NUMERIC(5,2) DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_factores_riesgo_zona
ON factores_riesgo_zona(id_zona);

CREATE TABLE eventos_seguridad (
    id_evento SERIAL PRIMARY KEY,

    tipo_evento VARCHAR(80) NOT NULL,
    descripcion TEXT,

    estado VARCHAR(50) DEFAULT 'activo',
    severidad INT DEFAULT 1,

    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    ubicacion GEOMETRY(POINT, 4326) NOT NULL,

    fecha_inicio TIMESTAMP DEFAULT NOW(),
    fecha_fin TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_eventos_ubicacion
ON eventos_seguridad
USING GIST (ubicacion);

CREATE INDEX idx_eventos_estado
ON eventos_seguridad(estado);

-- Tipos de eventos de seguridad
--robo_detectado
--persona_sospechosa
--agresion_detectada
--aglomeracion
--vehiculo_sospechoso

CREATE TABLE detecciones_camara (
    id_deteccion BIGSERIAL PRIMARY KEY,

    id_camara INT REFERENCES camaras(id_camara),
    id_evento INT REFERENCES eventos_seguridad(id_evento),

    clase_detectada VARCHAR(80) NOT NULL,
    confianza NUMERIC(5,4),

    tracking_id VARCHAR(120),

    bbox JSONB,
    metadata JSONB,

    fecha_deteccion TIMESTAMP DEFAULT NOW(),

    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    ubicacion GEOMETRY(POINT, 4326),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_detecciones_camara
ON detecciones_camara(id_camara);

CREATE INDEX idx_detecciones_evento
ON detecciones_camara(id_evento);

CREATE INDEX idx_detecciones_tracking
ON detecciones_camara(tracking_id);

CREATE INDEX idx_detecciones_ubicacion
ON detecciones_camara
USING GIST (ubicacion);

--Alimentar desde yolo con la deteccion de objetos en tiempo real, con clases como

CREATE TABLE rutas_calculadas (
    id_ruta BIGSERIAL PRIMARY KEY,

    tipo_ruta VARCHAR(80) NOT NULL,
    id_evento INT REFERENCES eventos_seguridad(id_evento),

    origen GEOMETRY(POINT, 4326) NOT NULL,
    destino GEOMETRY(POINT, 4326),

    score_riesgo NUMERIC(5,2),
    distancia_m DOUBLE PRECISION,
    duracion_estimada_seg DOUBLE PRECISION,

    algoritmo VARCHAR(80),
    parametros JSONB,

    geom GEOMETRY(LINESTRING, 4326),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rutas_geom
ON rutas_calculadas
USING GIST (geom);

CREATE INDEX idx_rutas_tipo
ON rutas_calculadas(tipo_ruta);

--ruta_segura_turista
--ruta_probable_desplazamiento
--ruta_cobertura_camaras
--ruta_respuesta_emergencia

CREATE TABLE rutas_segmentos (
    id_segmento BIGSERIAL PRIMARY KEY,

    id_ruta BIGINT REFERENCES rutas_calculadas(id_ruta),
    id_edge INT REFERENCES calles_edges(id_edge),

    orden INT NOT NULL,

    distancia_m DOUBLE PRECISION,
    riesgo_segmento NUMERIC(5,2),

    geom GEOMETRY(LINESTRING, 4326)
);

CREATE INDEX idx_rutas_segmentos_geom
ON rutas_segmentos
USING GIST (geom);

-Este tramo se evitó porque tiene reportes recientes.
-Este tramo es preferido porque tiene cámaras cerca.
-Este tramo es menos riesgoso por iluminación/reputación.

--Para la parte de Rutas seguras para el Mundial añadiendo un costo a cada una de las aristas basado en:
--menor riesgo
--distancia razonable
--mayor cobertura de cámaras
--calles principales
--cercanía a zonas turísticas
--menor historial de reportes
--mejor iluminación cuando exista el dato

Cuando una cámara detecta algo:

{
  "id_camara": 12,
  "clase_detectada": "person",
  "tracking_id": "abc-123",
  "confianza": 0.91,
  "fecha_deteccion": "2026-05-12T20:35:10"
}

El sistema hace:

1. Obtener ubicación de cámara.
2. Encontrar calles cercanas.
3. Buscar cámaras vecinas dentro de 300 m, 500 m, 1 km.
4. Calcular caminos posibles.
5. Ordenarlos por probabilidad.

Factores de probabilidad:

distancia desde última cámara
tiempo transcurrido
dirección aparente
calles principales
calles con baja cobertura
salidas de zona
detecciones anteriores del mismo tracking_id

Score inicial:

probabilidad =
  cercanía a última detección
+ coincidencia de tiempo
+ dirección de movimiento
+ continuidad por red vial
+ posibilidad de salida