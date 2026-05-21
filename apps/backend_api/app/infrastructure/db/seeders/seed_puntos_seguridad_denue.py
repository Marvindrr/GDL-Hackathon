import os

from geoalchemy2 import WKTElement

from app.infrastructure.clients.denue_client import DenueClient
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.geo_models import Municipio, Zona
from app.infrastructure.db.models.report_models import FuenteDatos
from app.infrastructure.db.models.security_point_models import PuntoSeguridad
from app.infrastructure.db.seeders.denue_mapper import (
    build_direccion,
    get_colonia,
    get_cp,
    get_denue_id,
    get_lat,
    get_lon,
    get_nombre,
    get_razon_social,
    get_sitio_web,
    get_telefono,
)


ENTIDAD_JALISCO = os.getenv("DENUE_ENTIDAD_JALISCO", "14")
PAGE_SIZE = int(os.getenv("DENUE_SEED_PAGE_SIZE", "200"))


MUNICIPIOS_JALISCO = {
    "Guadalajara": "039",
    "Zapopan": "120",
    "San Pedro Tlaquepaque": "098",
    "Tonalá": "101",
    "Tlajomulco de Zúñiga": "097",
    "El Salto": "070",
    "Tequila": "094",
}


MARCAS_SEGURAS = [
    {
        "query": "OXXO",
        "marca": "OXXO",
        "tipo_punto": "tienda_segura",
        "peso_seguridad": 12,
        "nivel_confianza": 70,
        "es_24h": True,
    },
    {
        "query": "FARMACIAS GUADALAJARA",
        "marca": "Farmacias Guadalajara",
        "tipo_punto": "farmacia_segura",
        "peso_seguridad": 16,
        "nivel_confianza": 75,
        "es_24h": False,
    },
# {
#     "query": "7 ELEVEN",
#     "marca": "7-Eleven",
#     "tipo_punto": "tienda_segura",
#     "peso_seguridad": 12,
#     "nivel_confianza": 70,
#     "es_24h": True,
# },

]


def point_wkt(lon, lat):
    return WKTElement(f"POINT({lon} {lat})", srid=4326)


def get_fuente_denue(db) -> FuenteDatos:
    fuente = (
        db.query(FuenteDatos)
        .filter(FuenteDatos.nombre == "INEGI_DENUE")
        .first()
    )

    if not fuente:
        fuente = FuenteDatos(
            nombre="INEGI_DENUE",
            tipo="negocios",
            descripcion="Fuente oficial para establecimientos, comercios, tiendas y servicios cercanos.",
            activa=True,
        )
        db.add(fuente)
        db.flush()

    return fuente


def get_municipio(db, nombre: str) -> Municipio:
    municipio = (
        db.query(Municipio)
        .filter(Municipio.nombre == nombre)
        .first()
    )

    if not municipio:
        municipio = Municipio(
            nombre=nombre,
            estado="Jalisco",
        )
        db.add(municipio)
        db.flush()

    return municipio


def buscar_zona_por_punto(db, lon, lat):
    """
    Si existe geometría de zona, intenta encontrar en qué zona cae el punto.
    Si tus colonias todavía solo tienen centro y no polígono, esto regresará None.
    """
    punto = point_wkt(lon, lat)

    return (
        db.query(Zona)
        .filter(Zona.geom.isnot(None))
        .filter(Zona.geom.ST_Contains(punto))
        .first()
    )


def normalizar_nombre_para_filtro(texto: str) -> str:
    return (
        (texto or "")
        .upper()
        .replace("-", " ")
        .replace("_", " ")
        .strip()
    )


def pertenece_a_marca(nombre: str, razon_social: str, marca: str) -> bool:
    texto = normalizar_nombre_para_filtro(f"{nombre} {razon_social}")
    marca_normalizada = normalizar_nombre_para_filtro(marca)

    if marca_normalizada in ("7 ELEVEN", "7-ELEVEN"):
        return "7 ELEVEN" in texto or "SEVEN ELEVEN" in texto

    if marca_normalizada == "FARMACIAS GUADALAJARA":
        return "FARMACIAS GUADALAJARA" in texto

    return marca_normalizada in texto


def upsert_punto_seguridad(
    db,
    fuente: FuenteDatos,
    municipio: Municipio,
    item_denue: dict,
    config_marca: dict,
    claves_procesadas: set[tuple[int, str]],
):
    id_externo = get_denue_id(item_denue)
    nombre = get_nombre(item_denue)
    razon_social = get_razon_social(item_denue)
    lat = get_lat(item_denue)
    lon = get_lon(item_denue)

    if not id_externo:
        return "omitido"

    clave_unica = (fuente.id_fuente, id_externo)

    # Evita duplicados que vienen repetidos desde DENUE en la misma ejecución.
    if clave_unica in claves_procesadas:
        return "duplicado_batch"

    if not nombre or lat is None or lon is None:
        claves_procesadas.add(clave_unica)
        return "omitido"

    if not pertenece_a_marca(
        nombre=nombre,
        razon_social=razon_social,
        marca=config_marca["marca"],
    ):
        claves_procesadas.add(clave_unica)
        return "omitido"

    zona = buscar_zona_por_punto(db, lon, lat)

    existente = (
        db.query(PuntoSeguridad)
        .filter(
            PuntoSeguridad.id_fuente == fuente.id_fuente,
            PuntoSeguridad.id_externo == id_externo,
        )
        .first()
    )

    direccion = build_direccion(item_denue)
    colonia = get_colonia(item_denue)
    codigo_postal = get_cp(item_denue)

    metadata = {
        "raw_denue": item_denue,
        "razon_social": razon_social,
        "origen_seed": "seed_puntos_seguridad_denue",
        "marca_query": config_marca["query"],
    }

    data = {
        "id_fuente": fuente.id_fuente,
        "id_municipio": municipio.id_municipio,
        "id_zona": zona.id_zona if zona else None,
        "id_externo": id_externo,
        "nombre": nombre,
        "marca": config_marca["marca"],
        "tipo_punto": config_marca["tipo_punto"],
        "direccion": direccion,
        "colonia": colonia,
        "codigo_postal": codigo_postal,
        "telefono": get_telefono(item_denue),
        "sitio_web": get_sitio_web(item_denue),
        "horario": None,
        "es_24h": config_marca["es_24h"],
        "lat": lat,
        "lon": lon,
        "ubicacion": point_wkt(lon, lat),
        "validado_c5": False,
        "activo": True,
        "nivel_confianza": config_marca["nivel_confianza"],
        "peso_seguridad": config_marca["peso_seguridad"],
        "extra_metadata": metadata,
    }

    if existente:
        for key, value in data.items():
            setattr(existente, key, value)

        claves_procesadas.add(clave_unica)
        return "actualizado"

    db.add(PuntoSeguridad(**data))
    claves_procesadas.add(clave_unica)

    return "insertado"


def seed_puntos_seguridad_denue():
    db = SessionLocal()
    client = DenueClient()

    total_insertados = 0
    total_actualizados = 0
    total_omitidos = 0
    total_duplicados_batch = 0

    # Sirve para evitar duplicados dentro de una misma corrida,
    # incluso antes de que SQLAlchemy haga commit.
    claves_procesadas: set[tuple[int, str]] = set()

    try:
        fuente = get_fuente_denue(db)

        for municipio_nombre, municipio_clave in MUNICIPIOS_JALISCO.items():
            municipio = get_municipio(db, municipio_nombre)

            print(f"\nMunicipio: {municipio_nombre} ({municipio_clave})")

            for config_marca in MARCAS_SEGURAS:
                print(f"  Consultando DENUE: {config_marca['query']}")

                try:
                    registros = client.buscar_todos_paginado(
                        entidad=ENTIDAD_JALISCO,
                        municipio=municipio_clave,
                        nombre=config_marca["query"],
                        page_size=PAGE_SIZE,
                        max_pages=20,
                    )
                except Exception as e:
                    print(f"  Error consultando {config_marca['query']}: {e}")
                    print("  Se omite esta marca y continúa la seed.")
                    db.rollback()
                    continue

                print(f"  Registros recibidos: {len(registros)}")

                insertados_batch = 0
                actualizados_batch = 0
                omitidos_batch = 0
                duplicados_batch = 0

                for item in registros:
                    resultado = upsert_punto_seguridad(
                        db=db,
                        fuente=fuente,
                        municipio=municipio,
                        item_denue=item,
                        config_marca=config_marca,
                        claves_procesadas=claves_procesadas,
                    )

                    if resultado == "insertado":
                        total_insertados += 1
                        insertados_batch += 1
                    elif resultado == "actualizado":
                        total_actualizados += 1
                        actualizados_batch += 1
                    elif resultado == "duplicado_batch":
                        total_duplicados_batch += 1
                        duplicados_batch += 1
                    else:
                        total_omitidos += 1
                        omitidos_batch += 1

                db.commit()

                print(
                    f"  Resultado {config_marca['query']}: "
                    f"insertados={insertados_batch}, "
                    f"actualizados={actualizados_batch}, "
                    f"omitidos={omitidos_batch}, "
                    f"duplicados_denue={duplicados_batch}"
                )

        print("\nSeed puntos_seguridad DENUE completado.")
        print(f"Insertados: {total_insertados}")
        print(f"Actualizados: {total_actualizados}")
        print(f"Omitidos: {total_omitidos}")
        print(f"Duplicados en respuesta DENUE: {total_duplicados_batch}")

    except Exception as e:
        db.rollback()
        print(f"Error en seed_puntos_seguridad_denue: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_puntos_seguridad_denue()