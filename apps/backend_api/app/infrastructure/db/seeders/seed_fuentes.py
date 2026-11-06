from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.report_models import FuenteDatos


FUENTES_INICIALES = [
    {
        "nombre": "JSON_COLONIAS_RIESGO_LOCAL",
        "tipo": "json_local",
        "descripcion": "Datos locales simulados de colonias con latitud, longitud y riesgo base.",
        "activa": True,
    },
    {
        "nombre": "JSON_PUNTOS_TURISTICOS_LOCAL",
        "tipo": "json_local",
        "descripcion": "Datos locales de puntos turísticos usados para rutas turísticas.",
        "activa": True,
    },
    {
        "nombre": "JSON_ZONAS_TURISTICAS_POLIGONOS_LOCAL",
        "tipo": "json_local",
        "descripcion": "Datos locales de zonas turísticas normalizadas con centro y polígono.",
        "activa": True,
    },
    {
        "nombre": "JSON_CAMARAS_LOCAL",
        "tipo": "json_local",
        "descripcion": "Datos locales de cámaras simuladas o precargadas.",
        "activa": True,
    },
    {
        "nombre": "SIMULACION_HACKATHON",
        "tipo": "simulacion",
        "descripcion": "Datos simulados para pruebas del hackathon y demostraciones locales.",
        "activa": True,
    },
    {
        "nombre": "OPERADOR_MANUAL",
        "tipo": "manual",
        "descripcion": "Datos capturados manualmente por un operador del sistema.",
        "activa": True,
    },
    {
        "nombre": "SISTEMA_YOLO",
        "tipo": "vision_artificial",
        "descripcion": "Detecciones generadas por modelos de visión artificial.",
        "activa": True,
    },
    {
        "nombre": "C5_ZAPOPAN",
        "tipo": "institucional",
        "descripcion": "Fuente futura para integración con C5 Zapopan.",
        "activa": False,
    },
    {
        "nombre": "WAZE_FOR_CITIES",
        "tipo": "trafico",
        "descripcion": "Fuente futura para tráfico, incidentes y cierres viales.",
        "activa": False,
    },
    {
        "nombre": "TOMTOM_TRAFFIC",
        "tipo": "trafico",
        "descripcion": "Fuente futura para tráfico, velocidades e incidentes viales.",
        "activa": False,
    },
    {
        "nombre": "HERE_TRAFFIC",
        "tipo": "trafico",
        "descripcion": "Fuente futura para tráfico e incidentes viales.",
        "activa": False,
    },
    {
        "nombre": "OPENSTREETMAP",
        "tipo": "mapa",
        "descripcion": "Fuente futura para calles, rutas, negocios, servicios y puntos de interés.",
        "activa": False,
    },
    {
        "nombre": "INEGI_DENUE",
        "tipo": "negocios",
        "descripcion": "Fuente futura para establecimientos, comercios y servicios cercanos.",
        "activa": False,
    },
    {
        "nombre": "SESNSP",
        "tipo": "seguridad_historica",
        "descripcion": "Fuente futura para incidencia delictiva histórica por municipio.",
        "activa": False,
    },
    {
        "nombre": "IIEG_JALISCO",
        "tipo": "seguridad_historica",
        "descripcion": "Fuente futura para datos estadísticos de seguridad de Jalisco.",
        "activa": False,
    },
    {
        "nombre": "OPEN_METEO",
        "tipo": "clima",
        "descripcion": "Fuente futura para clima, lluvia, visibilidad y contexto ambiental.",
        "activa": False,
    },
    {
    "nombre": "INEGI_DENUE",
    "tipo": "negocios",
    "descripcion": "Fuente oficial para establecimientos, comercios, tiendas y servicios cercanos.",
    "activa": True,
    },
    {
        "nombre": "SIMULACION_PUNTOS_SEGUROS",
        "tipo": "simulacion",
        "descripcion": "Puntos seguros simulados para pruebas y demostraciones.",
        "activa": True,
    },
    {
        "nombre": "C5_ZAPOPAN",
        "tipo": "institucional",
        "descripcion": "Fuente futura para puntos seguros, cámaras, botones de pánico y eventos del C5 Zapopan.",
        "activa": False,
    },
    {
        "nombre": "C5_JALISCO",
        "tipo": "institucional",
        "descripcion": "Fuente futura para botones de pánico e infraestructura de seguridad estatal.",
        "activa": False,
    },
    {
        "nombre": "CADENA_OXXO",
        "tipo": "cadena_comercial",
        "descripcion": "Fuente futura directa de tiendas OXXO consideradas puntos seguros.",
        "activa": False,
    },
    {
        "nombre": "CADENA_FARMACIAS_GUADALAJARA",
        "tipo": "cadena_comercial",
        "descripcion": "Fuente futura directa de Farmacias Guadalajara consideradas puntos seguros.",
        "activa": False,
    },
    {
        "nombre": "CADENA_7ELEVEN",
        "tipo": "cadena_comercial",
        "descripcion": "Fuente futura directa de 7-Eleven considerados puntos seguros.",
        "activa": False,
    },
]


def seed_fuentes():
    db = SessionLocal()

    try:
        for item in FUENTES_INICIALES:
            existente = (
                db.query(FuenteDatos)
                .filter(FuenteDatos.nombre == item["nombre"])
                .first()
            )

            if existente:
                existente.tipo = item["tipo"]
                existente.descripcion = item["descripcion"]
                existente.activa = item["activa"]
            else:
                db.add(FuenteDatos(**item))

        db.commit()
        print("Seed fuentes_datos completado.")
    except Exception as e:
        db.rollback()
        print(f"Error en seed_fuentes: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_fuentes()