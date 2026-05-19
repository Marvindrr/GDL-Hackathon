from pathlib import Path

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.geo_models import PuntoTuristico
from app.infrastructure.db.seeders.seed_helpers import (
    get_project_root,
    get_or_create_municipio,
    load_json_from_candidates,
    point_wkt,
)


def seed_puntos_turisticos():
    db = SessionLocal()
    root = get_project_root()

    frontend_legacy_dir = Path(
        str(root / "apps" / "frontend_legacy")
    )

    json_data = load_json_from_candidates([
        frontend_legacy_dir / "static" / "modules" / "gdl_turismo" / "data" / "gdl_puntos_turisticos_ruta.json",
        Path("/workspace/apps/frontend_legacy/static/modules/gdl_turismo/data/gdl_puntos_turisticos_ruta.json"),
    ])

    insertados = 0
    actualizados = 0

    try:
        for item in json_data:
            municipio_nombre = item.get("municipio")
            nombre = item.get("nombre")
            categoria = item.get("tipo", "punto_turistico")
            lat = item.get("lat")
            lon = item.get("lon")
            riesgo = item.get("riesgo")

            if not municipio_nombre or not nombre or lat is None or lon is None:
                continue

            municipio = get_or_create_municipio(db, municipio_nombre, "Jalisco")

            existente = (
                db.query(PuntoTuristico)
                .filter(
                    PuntoTuristico.id_municipio == municipio.id_municipio,
                    PuntoTuristico.nombre == nombre,
                )
                .first()
            )

            descripcion = f"Punto turístico cargado desde JSON local. Riesgo base referencial: {riesgo}"

            if existente:
                existente.categoria = categoria
                existente.descripcion = descripcion
                existente.lat = lat
                existente.lon = lon
                existente.ubicacion = point_wkt(lon, lat)
                existente.activo = True
                actualizados += 1
            else:
                db.add(PuntoTuristico(
                    id_municipio=municipio.id_municipio,
                    nombre=nombre,
                    categoria=categoria,
                    descripcion=descripcion,
                    lat=lat,
                    lon=lon,
                    ubicacion=point_wkt(lon, lat),
                    activo=True,
                ))
                insertados += 1

        db.commit()
        print(f"Seed puntos turísticos completado. Insertados: {insertados}, actualizados: {actualizados}")
    except Exception as e:
        db.rollback()
        print(f"Error en seed_puntos_turisticos: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_puntos_turisticos()    