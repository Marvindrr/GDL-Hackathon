Nuestro proyecto trata de un sistema inteligente de monitoreo para prevencion del delito, su funcion de este es mostar zonas de riesgo con su probabilidad de riesgo, tambien muestra rutas de escape, tambien muestra en graficas el numero de delitos que pasaron en cada mes y muestra si estas cantidades pueden disminuir, aumentar o establecerse con el mismo número de delitos,tambien cuenta con deteccion de ropa (calcetines, playeras y sueteres), todas estas virtudes de nuestro proyecto estan hechas con inteligencias artificiales las culaes nos dan una probabilidad de 95.7%.
Todo lo mencionado anteriormente lo hicimos con la finalidad de que sea un metodo más eficas, eficiente y efectivo para la prevencion de los delitos y asi tener en cuenta las rutas mas epecificas por las cuales los delincuentes suelen escapar, cabe mencionar que contamos con un factor sorpresa el cual es el que los delincuentes no sepan en que momento y por ruta seran interceptados por la policia, asi mismo con este metodo estamos evitando el daños a terceros, ya que suele pasar que en alguna persecución automovilistco suelen provocar un accidente y con nuestro proyecto prevee eso mismo.
Cabe mencionar que nuestro objetivo principal es darselo al C5 ya que si lo dejamos al publico puede llegar a manos equivocadas en este caso a los delincuentes.


Versión local recomendada: Python 3.13
Driver PostgreSQL: psycopg 3
Docker backend: Python 3.11 temporalmente

## 🗄️ Arquitectura de la Base de Datos (Entity-Relationship)

El sistema utiliza una base de datos relacional con capacidades espaciales (PostGIS) diseñada para manejar grandes volúmenes de telemetría de cámaras, análisis de IA en tiempo real y cálculo de rutas seguras mediante grafos.

```mermaid
erDiagram

    MUNICIPIOS ||--o{ ZONAS : contiene
    MUNICIPIOS ||--o{ PUNTOS_TURISTICOS : contiene
    MUNICIPIOS ||--o{ CAMARAS : contiene

    ZONAS ||--o{ FACTORES_RIESGO_ZONA : tiene
    ZONAS ||--o{ HISTORIAL_RIESGO_ZONA : registra
    ZONAS ||--o{ REPORTES_SEGURIDAD : recibe
    ZONAS ||--o{ EVENTOS_SEGURIDAD : ocurre_en
    ZONAS ||--o{ CALLES_EDGES : cruza

    CAMARAS ||--o{ CAMARA_STREAMS : tiene
    CAMARAS ||--o{ CAMARA_ESTADOS : registra
    CAMARAS ||--o{ CAMARA_COBERTURA : cubre
    CAMARAS ||--o{ DETECCIONES_CAMARA : genera
    CAMARAS ||--o{ TRACK_OBSERVACIONES : observa

    MODELOS_IA ||--o{ EJECUCIONES_MODELO : ejecuta
    MODELOS_IA ||--o{ DETECCIONES_CAMARA : produce
    MODELOS_IA ||--o{ COMPORTAMIENTOS_DETECTADOS : clasifica

    EVENTOS_SEGURIDAD ||--o{ DETECCIONES_CAMARA : agrupa
    EVENTOS_SEGURIDAD ||--o{ EVENTO_DETECCIONES : relaciona
    EVENTOS_SEGURIDAD ||--o{ RUTAS_CALCULADAS : genera
    EVENTOS_SEGURIDAD ||--o{ ALERTAS_SEGURIDAD : dispara
    EVENTOS_SEGURIDAD ||--o{ EVIDENCIAS_MEDIA : contiene

    DETECCIONES_CAMARA ||--o{ EVENTO_DETECCIONES : pertenece
    DETECCIONES_CAMARA ||--o{ EVIDENCIAS_MEDIA : tiene
    DETECCIONES_CAMARA ||--o{ COMPORTAMIENTOS_DETECTADOS : analiza
    DETECCIONES_CAMARA ||--o{ TRACK_OBSERVACIONES : registra

    TRACK_OBJETOS ||--o{ TRACK_OBSERVACIONES : tiene
    TRACK_OBJETOS ||--o{ EVENTOS_SEGURIDAD : puede_generar
    TRACK_OBJETOS ||--o{ RUTAS_CALCULADAS : genera

    CALLES_NODES ||--o{ CALLES_EDGES : origen
    CALLES_NODES ||--o{ CALLES_EDGES : destino
    CALLES_EDGES ||--o{ RUTAS_SEGMENTOS : compone

    RUTAS_CALCULADAS ||--o{ RUTAS_SEGMENTOS : contiene
    RUTAS_CALCULADAS ||--o{ RUTA_PUNTOS_CONTROL : tiene

    PUNTOS_TURISTICOS ||--o{ RUTAS_CALCULADAS : destino_turistico

    FUENTES_DATOS ||--o{ REPORTES_SEGURIDAD : alimenta
    FUENTES_DATOS ||--o{ FACTORES_RIESGO_ZONA : alimenta

    MUNICIPIOS {
        int id_municipio PK
        string nombre
        string estado
        geometry geom
        datetime created_at
    }

    ZONAS {
        int id_zona PK
        int id_municipio FK
        string nombre
        string tipo
        decimal riesgo_base
        decimal reputacion_base
        decimal nivel_luz_base
        geometry geom
        geometry centro
        datetime created_at
        datetime updated_at
    }

    CAMARAS {
        int id_camara PK
        int id_municipio FK
        int id_zona FK
        string nombre
        string codigo_externo
        string tipo
        string fuente
        decimal lat
        decimal lon
        geometry ubicacion
        string direccion_texto
        boolean activa
        datetime created_at
        datetime updated_at
    }

    CAMARA_STREAMS {
        int id_stream PK
        int id_camara FK
        string url_stream
        string protocolo
        string usuario
        string password_encrypted
        boolean activo
        datetime created_at
    }

    CAMARA_ESTADOS {
        bigint id_estado PK
        int id_camara FK
        string estado
        decimal fps_actual
        decimal latencia_ms
        string mensaje_error
        datetime fecha_estado
    }

    CAMARA_COBERTURA {
        int id_cobertura PK
        int id_camara FK
        decimal angulo
        decimal distancia_m
        geometry geom
        datetime created_at
    }

    MODELOS_IA {
        int id_modelo PK
        string nombre
        string version
        string tipo_modelo
        string proveedor
        string descripcion
        boolean activo
        datetime created_at
    }

    EJECUCIONES_MODELO {
        bigint id_ejecucion PK
        int id_modelo FK
        string estado
        datetime fecha_inicio
        datetime fecha_fin
        json parametros
        json metricas
    }

    DETECCIONES_CAMARA {
        bigint id_deteccion PK
        int id_camara FK
        int id_modelo FK
        int id_evento FK
        string clase_detectada
        decimal confianza
        string tracking_id_externo
        json bbox
        json keypoints
        json metadata
        datetime fecha_deteccion
        decimal lat
        decimal lon
        geometry ubicacion
        datetime created_at
    }

    TRACK_OBJETOS {
        bigint id_track PK
        string tracking_id
        string tipo_objeto
        string estado
        decimal confianza_global
        datetime fecha_inicio
        datetime fecha_fin
        geometry ultima_ubicacion
        datetime created_at
        datetime updated_at
    }

    TRACK_OBSERVACIONES {
        bigint id_observacion PK
        bigint id_track FK
        bigint id_deteccion FK
        int id_camara FK
        datetime fecha_observacion
        decimal lat
        decimal lon
        geometry ubicacion
        decimal velocidad_estimada_m_s
        decimal direccion_grados
        json metadata
    }

    COMPORTAMIENTOS_DETECTADOS {
        bigint id_comportamiento PK
        bigint id_deteccion FK
        int id_modelo FK
        string tipo_comportamiento
        decimal confianza
        decimal severidad
        json metadata
        datetime fecha_deteccion
    }

    EVENTOS_SEGURIDAD {
        int id_evento PK
        int id_zona FK
        bigint id_track FK
        string tipo_evento
        string descripcion
        string estado
        int severidad
        decimal lat
        decimal lon
        geometry ubicacion
        datetime fecha_inicio
        datetime fecha_fin
        datetime created_at
        datetime updated_at
    }

    EVENTO_DETECCIONES {
        bigint id_evento_deteccion PK
        int id_evento FK
        bigint id_deteccion FK
        string relacion
        datetime created_at
    }

    EVIDENCIAS_MEDIA {
        bigint id_evidencia PK
        int id_evento FK
        bigint id_deteccion FK
        string tipo_media
        string path_archivo
        string url_archivo
        datetime fecha_captura
        json metadata
        datetime created_at
    }

    ALERTAS_SEGURIDAD {
        bigint id_alerta PK
        int id_evento FK
        string tipo_alerta
        string prioridad
        string estado
        string mensaje
        datetime fecha_alerta
        datetime fecha_atencion
    }

    REPORTES_SEGURIDAD {
        int id_reporte PK
        int id_zona FK
        int id_fuente FK
        string tipo_reporte
        string descripcion
        int severidad
        decimal lat
        decimal lon
        geometry ubicacion
        boolean validado
        datetime fecha_reporte
        datetime created_at
    }

    FACTORES_RIESGO_ZONA {
        int id_factor PK
        int id_zona FK
        int id_fuente FK
        datetime fecha_inicio
        datetime fecha_fin
        decimal reportes_score
        decimal luz_score
        decimal reputacion_score
        decimal hora_score
        decimal camaras_score
        decimal flujo_personas_score
        decimal comportamiento_score
        decimal riesgo_total
        datetime created_at
    }

    HISTORIAL_RIESGO_ZONA {
        bigint id_historial PK
        int id_zona FK
        decimal riesgo_total
        json desglose
        string algoritmo
        datetime fecha_calculo
    }

    CALLES_NODES {
        bigint id_node PK
        geometry geom
    }

    CALLES_EDGES {
        bigint id_edge PK
        bigint source FK
        bigint target FK
        int id_zona FK
        string nombre
        string tipo_via
        decimal distancia_m
        decimal velocidad_estimada_kmh
        decimal riesgo_base
        decimal costo_base
        geometry geom
        datetime created_at
    }

    RUTAS_CALCULADAS {
        bigint id_ruta PK
        int id_evento FK
        bigint id_track FK
        int id_punto_turistico FK
        string tipo_ruta
        geometry origen
        geometry destino
        decimal score_riesgo
        decimal score_confianza
        decimal distancia_m
        decimal duracion_estimada_seg
        string algoritmo
        json parametros
        geometry geom
        datetime created_at
    }

    RUTAS_SEGMENTOS {
        bigint id_segmento PK
        bigint id_ruta FK
        bigint id_edge FK
        int orden
        decimal distancia_m
        decimal riesgo_segmento
        decimal costo_segmento
        geometry geom
    }

    RUTA_PUNTOS_CONTROL {
        bigint id_punto_control PK
        bigint id_ruta FK
        int orden
        string tipo_punto
        string descripcion
        geometry ubicacion
        datetime created_at
    }

    PUNTOS_TURISTICOS {
        int id_punto_turistico PK
        int id_municipio FK
        string nombre
        string categoria
        string descripcion
        decimal lat
        decimal lon
        geometry ubicacion
        boolean activo
        datetime created_at
    }

    FUENTES_DATOS {
        int id_fuente PK
        string nombre
        string tipo
        string descripcion
        boolean activa
        datetime created_at
    }