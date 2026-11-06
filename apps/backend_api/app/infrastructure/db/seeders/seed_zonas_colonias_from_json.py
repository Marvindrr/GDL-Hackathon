from pathlib import Path

from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models.geo_models import Zona
from app.infrastructure.db.seeders.seed_helpers import (
    get_project_root,
    get_or_create_municipio,
    load_json_from_candidates,
    point_wkt,
)


def seed_zonas_colonias():
    db = SessionLocal()
    root = get_project_root()

    json_data = load_json_from_candidates([
        root / "data" / "gdl_turismo" / "gdl_colonias_jalisco.json",
        root / "data" / "geo" / "gdl_colonias_jalisco.json",
        Path("/workspace/data/gdl_turismo/gdl_colonias_jalisco.json"),
    ])

    insertadas = 0
    actualizadas = 0

    try:
        for item in json_data:
            municipio_nombre = item.get("municipio")
            nombre_colonia = item.get("nombre_colonia")
            estado = item.get("estado", "Jalisco")
            lat = item.get("lat")
            lon = item.get("lon")
            riesgo = item.get("riesgo", 0)

            if not municipio_nombre or not nombre_colonia or lat is None or lon is None:
                continue

            municipio = get_or_create_municipio(db, municipio_nombre, estado)

            existente = (
                db.query(Zona)
                .filter(
                    Zona.id_municipio == municipio.id_municipio,
                    Zona.nombre == nombre_colonia,
                    Zona.tipo == "colonia",
                )
                .first()
            )

            if existente:
                existente.riesgo_base = riesgo
                existente.centro = point_wkt(lon, lat)
                existente.reputacion_base = 50
                existente.nivel_luz_base = None
                actualizadas += 1
            else:
                db.add(Zona(
                    id_municipio=municipio.id_municipio,
                    nombre=nombre_colonia,
                    tipo="colonia",
                    riesgo_base=riesgo,
                    reputacion_base=50,
                    nivel_luz_base=None,
                    centro=point_wkt(lon, lat),
                    geom=None,
                ))
                insertadas += 1

        db.commit()
        print(f"Seed colonias completado. Insertadas: {insertadas}, actualizadas: {actualizadas}")
    except Exception as e:
        db.rollback()
        print(f"Error en seed_zonas_colonias: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_zonas_colonias()