import os

from geoalchemy2 import WKTElement

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.camera_models import Camara, CamaraStream
from app.infrastructure.db.models.geo_models import Municipio


def point_wkt(lon, lat):
    return WKTElement(f"POINT({lon} {lat})", srid=4326)


def get_or_create_municipio(db, nombre: str = "Guadalajara") -> Municipio:
    municipio = (
        db.query(Municipio)
        .filter(Municipio.nombre == nombre)
        .first()
    )

    if municipio:
        return municipio

    municipio = Municipio(nombre=nombre, estado="Jalisco")
    db.add(municipio)
    db.flush()

    return municipio


def upsert_camera_stream(db, camara: Camara, url_stream: str, protocolo: str):
    existente = (
        db.query(CamaraStream)
        .filter(
            CamaraStream.id_camara == camara.id_camara,
            CamaraStream.protocolo == protocolo,
        )
        .first()
    )

    if existente:
        existente.url_stream = url_stream
        existente.activo = True
        return existente

    stream = CamaraStream(
        id_camara=camara.id_camara,
        url_stream=url_stream,
        protocolo=protocolo,
        usuario=None,
        password_encrypted=None,
        activo=True,
    )

    db.add(stream)
    return stream


def seed_camaras_prueba():
    db = SessionLocal()

    try:
        municipio_nombre = os.getenv("LAB_CAMERA_MUNICIPIO", "Guadalajara")
        lat = float(os.getenv("LAB_CAMERA_LAT", "20.677055"))
        lon = float(os.getenv("LAB_CAMERA_LON", "-103.347063"))

        municipio = get_or_create_municipio(db, municipio_nombre)

        codigo = "WEBCAM_LAPTOP_LAB"

        camara = (
            db.query(Camara)
            .filter(Camara.codigo_externo == codigo)
            .first()
        )

        data = {
            "id_municipio": municipio.id_municipio,
            "id_zona": None,
            "nombre": "Webcam Laptop Laboratorio",
            "codigo_externo": codigo,
            "tipo": "laboratorio",
            "fuente": "webcam_local",
            "lat": lat,
            "lon": lon,
            "ubicacion": point_wkt(lon, lat),
            "direccion_texto": "Cámara de laptop usada para pruebas locales.",
            "activa": True,
        }

        if camara:
            for key, value in data.items():
                setattr(camara, key, value)
            print("Cámara webcam actualizada.")
        else:
            camara = Camara(**data)
            db.add(camara)
            db.flush()
            print("Cámara webcam insertada.")

        upsert_camera_stream(
            db=db,
            camara=camara,
            url_stream="webcam://0",
            protocolo="WEBCAM",
        )

        db.commit()

        print("Seed cámaras de prueba completado.")
        print(f"Código cámara: {codigo}")
        print(f"Ubicación simulada: lat={lat}, lon={lon}")

    except Exception as e:
        db.rollback()
        print(f"Error en seed_camaras_prueba: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_camaras_prueba()