
from geoalchemy2 import WKTElement

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.geo_models import Municipio
from app.infrastructure.db.models.report_models import FuenteDatos
from app.infrastructure.db.models.security_point_models import PuntoSeguridad


PUNTOS_SEGURIDAD_MANUALES = [
    {
        "id_externo": "SIM_OXXO_CENTRO_001",
        "municipio": "Guadalajara",
        "nombre": "OXXO Centro Histórico Simulado",
        "marca": "OXXO",
        "tipo_punto": "tienda_segura",
        "lat": 20.6768,
        "lon": -103.3469,
        "direccion": "Centro Histórico, Guadalajara",
        "es_24h": True,
        "peso_seguridad": 12,
    },
    {
        "id_externo": "SIM_FG_CENTRO_001",
        "municipio": "Guadalajara",
        "nombre": "Farmacias Guadalajara Centro Simulada",
        "marca": "Farmacias Guadalajara",
        "tipo_punto": "farmacia_segura",
        "lat": 20.6777,
        "lon": -103.3449,
        "direccion": "Centro Histórico, Guadalajara",
        "es_24h": False,
        "peso_seguridad": 16,
    },
    {
        "id_externo": "SIM_BP_CENTRO_001",
        "municipio": "Guadalajara",
        "nombre": "Botón de pánico Centro Simulado",
        "marca": "C5",
        "tipo_punto": "boton_panico",
        "lat": 20.6762,
        "lon": -103.3472,
        "direccion": "Centro Histórico, Guadalajara",
        "es_24h": True,
        "peso_seguridad": 25,
    },
    {
        "id_externo": "SIM_7E_AKRON_001",
        "municipio": "Zapopan",
        "nombre": "7-Eleven Estadio Akron Simulado",
        "marca": "7-Eleven",
        "tipo_punto": "tienda_segura",
        "lat": 20.6830,
        "lon": -103.4627,
        "direccion": "Zona Estadio Akron, Zapopan",
        "es_24h": True,
        "peso_seguridad": 12,
    },
]


def point_wkt(lon, lat):
    return WKTElement(f"POINT({lon} {lat})", srid=4326)


def get_fuente(db):
    fuente = (
        db.query(FuenteDatos)
        .filter(FuenteDatos.nombre == "SIMULACION_PUNTOS_SEGUROS")
        .first()
    )

    if not fuente:
        fuente = FuenteDatos(
            nombre="SIMULACION_PUNTOS_SEGUROS",
            tipo="simulacion",
            descripcion="Puntos seguros simulados para pruebas y demostraciones.",
            activa=True,
        )
        db.add(fuente)
        db.flush()

    return fuente


def get_municipio(db, nombre):
    municipio = (
        db.query(Municipio)
        .filter(Municipio.nombre == nombre)
        .first()
    )

    if not municipio:
        municipio = Municipio(nombre=nombre, estado="Jalisco")
        db.add(municipio)
        db.flush()

    return municipio


def seed_puntos_seguridad_manual():
    db = SessionLocal()

    try:
        fuente = get_fuente(db)

        insertados = 0
        actualizados = 0

        for item in PUNTOS_SEGURIDAD_MANUALES:
            municipio = get_municipio(db, item["municipio"])

            existente = (
                db.query(PuntoSeguridad)
                .filter(
                    PuntoSeguridad.id_fuente == fuente.id_fuente,
                    PuntoSeguridad.id_externo == item["id_externo"],
                )
                .first()
            )

            data = {
                "id_fuente": fuente.id_fuente,
                "id_municipio": municipio.id_municipio,
                "id_externo": item["id_externo"],
                "nombre": item["nombre"],
                "marca": item["marca"],
                "tipo_punto": item["tipo_punto"],
                "direccion": item["direccion"],
                "lat": item["lat"],
                "lon": item["lon"],
                "ubicacion": point_wkt(item["lon"], item["lat"]),
                "es_24h": item["es_24h"],
                "validado_c5": False,
                "activo": True,
                "nivel_confianza": 55,
                "peso_seguridad": item["peso_seguridad"],
                "extra_metadata": {
                    "origen_seed": "seed_puntos_seguridad_manual",
                    "nota": "Punto simulado para demostración.",
                },
            }

            if existente:
                for key, value in data.items():
                    setattr(existente, key, value)
                actualizados += 1
            else:
                db.add(PuntoSeguridad(**data))
                insertados += 1

        db.commit()

        print("Seed puntos_seguridad manual completado.")
        print(f"Insertados: {insertados}")
        print(f"Actualizados: {actualizados}")

    except Exception as e:
        db.rollback()
        print(f"Error en seed_puntos_seguridad_manual: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_puntos_seguridad_manual()